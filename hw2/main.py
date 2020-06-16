import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
import ibm_db
import geocoder
import geopy.distance
from config import *

app = Flask(__name__)

if 'VCAP_SERVICES' in os.environ:
    db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB For Transactions'][0]
    db2cred = db2info["credentials"]
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    raise ValueError('Expected cloud environment')



# main page to dump some environment information
@app.route('/')
def index():
   return render_template('index.html', app=appenv)



# for testing purposes - use name in URI
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/search_largest_n', methods=['GET'])
def largest_n(number=5):
    number = request.args.get('number', '')
    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE ORDER BY MAG DESC FETCH FIRST ? ROWS ONLY;"
        stmt = ibm_db.prepare(db2conn, sql)
        ibm_db.bind_param(stmt, 1, number)
        ibm_db.execute(stmt)
        
        rows=[]
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        
        ibm_db.close(db2conn)
    return render_template('large_n.html', ci=rows)



@app.route('/search_around_place', methods=['GET'])
def search_around_place():
    distance = request.args.get('distance', 500)
    city = request.args.get('city', 'arlington')
    
    usr_g_json = geocoder.osm(city).json
    trgt_coords = (usr_g_json['lat'], usr_g_json['lng'])

    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        rows=[]
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_coords = (result['LATITUDE'], result['LONGTITUDE'])
            if geopy.distance.vincenty(curr_coords, trgt_coords).km<distance:
                rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        
        ibm_db.close(db2conn)
    return render_template('search_around_place.html', ci=rows)



@app.route('/count_scale', methods=['GET'])
def count_scale():
    start = request.args.get('start', default='2020-06-01')
    end = request.args.get('end', default='2020-06-01')
    start = '2020-06-01' if start=='' else start
    end = '2020-06-08' if end=='' else end
    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    end = datetime.datetime.strptime(end, "%Y-%m-%d")
    scale = request.args.get('scale', '3')

    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE WHERE MAGTYPE=\'ml\' AND MAG>=?"
        stmt = ibm_db.prepare(db2conn, sql)
        ibm_db.bind_param(stmt, 1, scale)
        ibm_db.execute(stmt)
        
        rows=[]
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_date = result['TIME'][:10]
            curr_date = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
            if start<=curr_date<=end:
                rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
    
        ibm_db.close(db2conn)
    return render_template('count_scale.html', ci=rows)

@app.route('/search_scale', methods=['GET'])
def search_scale():
    number = request.args.get('number', 1000, type=int)
    today = datetime.date.today()
    ago = today - datetime.timedelta(days=number)
    
    slot12, slot23, slot34, slot45, slot56, slot67 = 0, 0, 0, 0, 0, 0
    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE WHERE MAGTYPE=\'ml\'"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_date = result['TIME'][:10]
            curr_date = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
            if curr_date.date()>=ago:
                print(curr_date)
                mag_scale = float(result['MAG'])
                if 1<=mag_scale<=2:
                    slot12 += 1
                if 2<=mag_scale<=3:
                    slot23 += 1
                if 3<=mag_scale<=4:
                    slot34 += 1
                if 4<=mag_scale<=5:
                    slot45 += 1
                if 5<=mag_scale<=6:
                    slot56 += 1
                if 6<=mag_scale<=7:
                    slot67 += 1
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    return render_template('search_scale.html', ci=[slot12, slot23, slot34, slot45, slot56, slot67])



@app.route('/compare_two_place', methods=['GET'])
def compare_two_place():
    distance = request.args.get('distance', 1000, type=int)
    
    placeA, placeB = request.args.get('placeA'), request.args.get('placeB')
    placeA = 'Anchorage' if placeA=='' else placeA
    placeB = 'Dallas' if placeB=='' else placeB
    
    pA_json, pB_json = geocoder.osm(placeA).json, geocoder.osm(placeB).json
    trgtA_coords, trgtB_coords = (pA_json['lat'], pA_json['lng']), (pB_json['lat'], pB_json['lng'])

    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        ansA, ansB = [], []
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_coords = (result['LATITUDE'], result['LONGTITUDE'])
            if geopy.distance.vincenty(curr_coords, trgtA_coords).km<distance:
                ansA.append(result.copy())
            if geopy.distance.vincenty(curr_coords, trgtB_coords).km<distance:
                ansB.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    print(len(ansA), len(ansB))
    return render_template('compare_two_place.html', ciA=ansA, ciB=ansB, pA=placeA, pB=placeB)



@app.route('/largest_around_place', methods=['GET'])
def largest_around_place():
    distance = request.args.get('distance', 500, type=int)
    city = request.args.get('city')
    city = 'Dallas' if city=='' else city
    usr_g_json = geocoder.osm(city).json
    trgt_coords = (usr_g_json['lat'], usr_g_json['lng'])

    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        ans, largest = [], 0
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_coords = (result['LATITUDE'], result['LONGTITUDE'])
            if geopy.distance.vincenty(curr_coords, trgt_coords).km<distance and float(result['MAG'])>largest:
                largest = float(result['MAG'])
                ans = [result.copy()]
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    return render_template('largest_around_place.html', ci=ans)



port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
