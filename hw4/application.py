import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
import ibm_db
import geocoder
import geopy.distance
from config import *
import time
import pandas as pd

app = Flask(__name__)

if 'VCAP_SERVICES' in os.environ:
    db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB For Transactions'][0]
    db2cred = db2info["credentials"]
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    raise ValueError('Expected cloud environment')

@app.route('/')
def index():
   return render_template('index.html', app=appenv)



@app.route('/search_largest_n', methods=['GET'])
def largest_n():
    number = request.args.get('number') if request.args.get('number') else 5
    slot01, slot12, slot23, slot34, slot45, slot56, slot67 = 0, 0, 0, 0, 0, 0, 0
    scatter_attr = []
    
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
            mag_scale = float(result['MAG'])
            if 0<=mag_scale<=1:
                slot01 += 1
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
            rows.append(result.copy())
            scatter_attr.append({"MAG": float(result['MAG']), "DEPTH": float(result['DEPTH'])})
            result = ibm_db.fetch_assoc(stmt)
        ibm_db.close(db2conn)
    print(scatter_attr)
    return render_template('large_n.html', rows=rows, sa=scatter_attr, ci={"0-1": slot01,
                                                                           "1-2": slot12, 
                                                                           "2-3": slot23, 
                                                                           "3-4": slot34, 
                                                                           "4-5": slot45, 
                                                                           "5-6": slot56, 
                                                                           "6-7": slot67})



@app.route('/search_around_place', methods=['GET'])
def search_around_place():
    distance = request.args.get('distance', 500)
    city = request.args.get('city', 'arlington')
    
    usr_g_json = geocoder.osm(city).json
    trgt_coords = (usr_g_json['lat'], usr_g_json['lng'])
    
    slot01, slot12, slot23, slot34, slot45, slot56, slot67 = 0, 0, 0, 0, 0, 0, 0
    scatter_attr = []

    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        rows=[]
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            try:
                curr_coords = (result['LATITUDE'], result['LONGTITUDE'])
                if geopy.distance.vincenty(curr_coords, trgt_coords).km<distance:
                    rows.append(result.copy())
                    scatter_attr.append({"MAG": float(result['MAG']), "DEPTH": float(result['DEPTH'])})
                    mag_scale = float(result['MAG'])
                    if 0<=mag_scale<=1:
                        slot01 += 1
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
            except:
                result = ibm_db.fetch_assoc(stmt)
        ibm_db.close(db2conn)
    return render_template('search_around_place.html', rows=rows, sa=scatter_attr, ci={"0-1": slot01,
                                                                                       "1-2": slot12, 
                                                                                       "2-3": slot23, 
                                                                                       "3-4": slot34, 
                                                                                       "4-5": slot45, 
                                                                                       "5-6": slot56, 
                                                                                       "6-7": slot67})



@app.route('/count_scale', methods=['GET'])
def count_scale():
    start = request.args.get('start', default='2020-06-01')
    end = request.args.get('end', default='2020-06-01')
    start = '2020-06-01' if start=='' else start
    end = '2020-06-08' if end=='' else end
    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    end = datetime.datetime.strptime(end, "%Y-%m-%d")
    scale = request.args.get('scale', '3')
    slot01, slot12, slot23, slot34, slot45, slot56, slot67 = 0, 0, 0, 0, 0, 0, 0
    scatter_attr = []

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
                mag_scale = float(result['MAG'])
                if 0<=mag_scale<=1:
                    slot01 += 1
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
                scatter_attr.append({"MAG": float(result['MAG']), "DEPTH": float(result['DEPTH'])})
                rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
    
        ibm_db.close(db2conn)
    
    return render_template('count_scale.html', rows=rows, sa=scatter_attr, ci={"0-1": slot01,
                                                                               "1-2": slot12, 
                                                                               "2-3": slot23, 
                                                                               "3-4": slot34, 
                                                                               "4-5": slot45, 
                                                                               "5-6": slot56, 
                                                                               "6-7": slot67})

@app.route('/search_scale', methods=['GET'])
def search_scale():
    number = request.args.get('number', 1000, type=int)
    today = datetime.date.today()
    ago = today - datetime.timedelta(days=number)
    slot01, slot12, slot23, slot34, slot45, slot56, slot67 = 0, 0, 0, 0, 0, 0, 0
    scatter_attr = []
    
    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE WHERE MAGTYPE=\'ml\'"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        # fetch the result
        rows=[]
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_date = result['TIME'][:10]
            curr_date = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
            if curr_date.date()>=ago:
                rows.append(result.copy())
                scatter_attr.append({"MAG": float(result['MAG']), "DEPTH": float(result['DEPTH'])})
                mag_scale = float(result['MAG'])
                if 0<=mag_scale<=1:
                    slot01 += 1
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
        
    return render_template('search_scale.html', rows=rows, sa=scatter_attr, ci={"0-1": slot01,
                                                                                "1-2": slot12, 
                                                                                "2-3": slot23, 
                                                                                "3-4": slot34, 
                                                                                "4-5": slot45, 
                                                                                "5-6": slot56, 
                                                                                "6-7": slot67})


port = os.getenv('PORT', '5001')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

""" Ref
1. [D3v5 map example](http://bl.ocks.org/almccon/1bcde7452450c153d8a0684085f249fd)
2. [Interactive Bar Chart Pie Chart](http://bl.ocks.org/cflavs/695d3215ccbce135d3bd)
"""