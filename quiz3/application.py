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
from cachetools import cached, Cache
import pandas as pd

app = Flask(__name__)
cache = Cache(maxsize=1000000)

@cached(cache)
def load_csv(fname, ftype):
    df = pd.read_csv('./static/{}.{}'.format(fname, ftype))
    return df



@cached(cache)
def save_file(fname):
    f = open('./static/{}.txt'.format(fname), 'w')
    return f



cache_sp = load_csv('sp', 'csv')
cache_pc = load_csv('pc', 'csv')

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



@app.route('/show_prev')
def show_prev():
    mode = request.args.get('mode1') if request.args.get('mode1') else request.args.get('mode2')
    mode = mode.split(' ')[0]
    start = time.time()
    country_code = request.args.get('code')
    rows=[]
    print('qqqq', country_code)
    
    if mode=='RDB':
        db2conn = ibm_db.connect(db2cred['ssldsn'], "","")    
        if db2conn:
            sql = "SELECT * FROM SP WHERE CODE=\'{}\';".format(country_code)
            stmt = ibm_db.exec_immediate(db2conn, sql)
            
            result = ibm_db.fetch_assoc(stmt)
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(stmt)
            
            ibm_db.close(db2conn)
            
    elif mode=='Memcache':
        global cache_sp
        df = cache_sp[cache_sp['CODE']==country_code]
        for _, r in df.iterrows():
            rows.append(r.to_dict())
        
    end = time.time()
    elapse = end - start

    return render_template('show_prev.html', app=appenv, rows=rows, e=elapse)



@app.route('/show_cost')
def show_cost():
    mode = request.args.get('mode1') if request.args.get('mode1') else request.args.get('mode2')
    mode = mode.split(' ')[-1]
    
    code = request.args.get('code') if request.args.get('code') else -1
    name = request.args.get('name') if request.args.get('name') else -1 
    times = request.args.get('time') if request.args.get('time') else 1 
    print('zzz', code, time)
    subsql = ''
    if code != -1:
        subsql += 'CODE=\'{}\''.format(code)
    if name != -1:
        subsql += ' AND ENTITY=\'{}\''.format(name)
    print('wwww', subsql, mode)
    rows1 = []
    rows2 = []
    
    start = time.time()
    for _ in range(int(times)):
        # connect to DB2
        if mode=='RDB':
            db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
            if db2conn:
                sql = "SELECT * FROM PC WHERE {};".format(subsql)
                print(sql)
                stmt = ibm_db.exec_immediate(db2conn, sql)
                
                result = ibm_db.fetch_assoc(stmt)
                while result != False:
                    rows1.append(result.copy())
                    result = ibm_db.fetch_assoc(stmt)
                    
                sql = "SELECT * FROM SP WHERE {};".format(subsql)
                print(sql)
                stmt = ibm_db.exec_immediate(db2conn, sql)
                
                result = ibm_db.fetch_assoc(stmt)
                while result != False:
                    rows2.append(result.copy())
                    result = ibm_db.fetch_assoc(stmt)

                ibm_db.close(db2conn)
        
        elif mode=='Memcache':
            global cache_pc
            if code != -1:
                df1 = cache_pc[cache_pc['CODE']==code]
                for _, r in df1.iterrows():
                    rows1.append(r.to_dict())
                
                df1 = cache_sp[cache_sp['CODE']==code]
                for _, r in df1.iterrows():
                    rows2.append(r.to_dict())
            if name != -1:
                df2 = cache_pc[cache_pc['ENTITY']==name]
                for _, r in df2.iterrows():
                    rows1.append(r.to_dict())
                df2 = cache_sp[cache_sp['CODE']==code]
                for _, r in df1.iterrows():
                    rows2.append(r.to_dict())
            
    end = time.time()
    elapse = end - start    
    return render_template('show_cost.html', app=appenv, rows1=rows1, rows2=rows2, e=elapse)



@app.route('/show_range')
def show_range():
    mode = request.args.get('mode1') if request.args.get('mode1') else request.args.get('mode2')
    mode = mode.split(' ')[-1]
    
    range0 = request.args.get('range0') if request.args.get('range0') else -1
    range1 = request.args.get('range1') if request.args.get('range1') else -1
    cost0 = request.args.get('cost0') if request.args.get('cost0') else -1 
    cost1 = request.args.get('cost1') if request.args.get('cost1') else -1 
    times = request.args.get('time') if request.args.get('time') else 1 
    print('zzz', range0, range1, cost0, cost1)
    subsql0 = ''
    subsql1 = ''
    if range0!=-1 and range1!=-1:
        subsql0 += 'YEAR>={} AND YEAR<={}'.format(range0, range1)
    if cost0!=-1 and cost1!=-1:
        subsql1 += 'COST>={} AND COST<=\'{}\''.format(cost0, cost1)
    print('wwww', subsql0, subsql1)
    rows1 = []
    rows2 = []
    
    start = time.time()
    for _ in range(int(times)):
        # connect to DB2
        if mode=='RDB':
            db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
            if db2conn:
                sql = "SELECT * FROM PC WHERE {} AND {};".format(subsql0, subsql1)
                print(sql)
                stmt = ibm_db.exec_immediate(db2conn, sql)
                
                result = ibm_db.fetch_assoc(stmt)
                while result != False:
                    rows1.append(result.copy())
                    result = ibm_db.fetch_assoc(stmt)
                    
                sql = "SELECT * FROM SP WHERE {};".format(subsql0)
                print(sql)
                stmt = ibm_db.exec_immediate(db2conn, sql)
                
                result = ibm_db.fetch_assoc(stmt)
                while result != False:
                    rows2.append(result.copy())
                    result = ibm_db.fetch_assoc(stmt)

                ibm_db.close(db2conn)
                print(rows1, rows2)
        
        elif mode=='Memcache':
            pass
            
    end = time.time()
    elapse = end - start    
    return render_template('show_range.html', app=appenv, rows1=rows1, rows2=rows2, e=elapse)




# @app.route('/count_scale', methods=['GET'])
# def count_scale():
#     st = time.time()
#     start = request.args.get('start', default='2020-06-01')
#     end = request.args.get('end', default='2020-06-01')
#     start = '2020-06-01' if start=='' else start
#     end = '2020-06-08' if end=='' else end
#     start = datetime.datetime.strptime(start, "%Y-%m-%d")
#     end = datetime.datetime.strptime(end, "%Y-%m-%d")
#     scale = request.args.get('scale', '3')

#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM EARTHQUAKE WHERE MAGTYPE=\'ml\' AND MAG>=?"
#         stmt = ibm_db.prepare(db2conn, sql)
#         ibm_db.bind_param(stmt, 1, scale)
#         ibm_db.execute(stmt)
        
#         rows=[]
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             curr_date = result['TIME'][:10]
#             curr_date = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
#             if start<=curr_date<=end:
#                 rows.append(result.copy())
#             result = ibm_db.fetch_assoc(stmt)
    
#         ibm_db.close(db2conn)
    
#     et = time.time()
#     elapse = et - st
#     return render_template('count_scale.html', ci=rows, elapse=elapse)

# @app.route('/search_scale', methods=['GET'])
# def search_scale():
#     start = time.time()
#     number = request.args.get('number', 1000, type=int)
#     today = datetime.date.today()
#     ago = today - datetime.timedelta(days=number)
    
#     slot12, slot23, slot34, slot45, slot56, slot67 = 0, 0, 0, 0, 0, 0
#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM EARTHQUAKE WHERE MAGTYPE=\'ml\'"
#         stmt = ibm_db.exec_immediate(db2conn, sql)
#         # fetch the result
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             curr_date = result['TIME'][:10]
#             curr_date = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
#             if curr_date.date()>=ago:
#                 print(curr_date)
#                 mag_scale = float(result['MAG'])
#                 if 1<=mag_scale<=2:
#                     slot12 += 1
#                 if 2<=mag_scale<=3:
#                     slot23 += 1
#                 if 3<=mag_scale<=4:
#                     slot34 += 1
#                 if 4<=mag_scale<=5:
#                     slot45 += 1
#                 if 5<=mag_scale<=6:
#                     slot56 += 1
#                 if 6<=mag_scale<=7:
#                     slot67 += 1
#             result = ibm_db.fetch_assoc(stmt)
#         # close database connection
#         ibm_db.close(db2conn)
#     end = time.time()
#     elapse = end - start
#     return render_template('search_scale.html', ci=[slot12, slot23, slot34, slot45, slot56, slot67], elapse=elapse)



# @app.route('/compare_two_place', methods=['GET'])
# def compare_two_place():
#     start = time.time()
#     distance = request.args.get('distance', 1000, type=int)
    
#     placeA, placeB = request.args.get('placeA'), request.args.get('placeB')
#     placeA = 'Anchorage' if placeA=='' else placeA
#     placeB = 'Dallas' if placeB=='' else placeB
    
#     pA_json, pB_json = geocoder.osm(placeA).json, geocoder.osm(placeB).json
#     trgtA_coords, trgtB_coords = (pA_json['lat'], pA_json['lng']), (pB_json['lat'], pB_json['lng'])

#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM EARTHQUAKE"
#         stmt = ibm_db.exec_immediate(db2conn, sql)
#         ansA, ansB = [], []
#         # fetch the result
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             curr_coords = (result['LATITUDE'], result['LONGTITUDE'])
#             if geopy.distance.vincenty(curr_coords, trgtA_coords).km<distance:
#                 ansA.append(result.copy())
#             if geopy.distance.vincenty(curr_coords, trgtB_coords).km<distance:
#                 ansB.append(result.copy())
#             result = ibm_db.fetch_assoc(stmt)
#         # close database connection
#         ibm_db.close(db2conn)
    
#     end = time.time()
#     elapse = end - start
#     return render_template('compare_two_place.html', ciA=ansA, ciB=ansB, pA=placeA, pB=placeB, elapse=elapse)



# @app.route('/largest_around_place', methods=['GET'])
# def largest_around_place():
#     start = time.time()
#     distance = request.args.get('distance', 500, type=int)
#     city = request.args.get('city')
#     city = 'Dallas' if city=='' else city
#     usr_g_json = geocoder.osm(city).json
#     trgt_coords = (usr_g_json['lat'], usr_g_json['lng'])

#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM EARTHQUAKE"
#         stmt = ibm_db.exec_immediate(db2conn, sql)
#         ans, largest = [], 0
#         # fetch the result
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             curr_coords = (result['LATITUDE'], result['LONGTITUDE'])
#             if geopy.distance.vincenty(curr_coords, trgt_coords).km<distance and float(result['MAG'])>largest:
#                 largest = float(result['MAG'])
#                 ans = [result.copy()]
#             result = ibm_db.fetch_assoc(stmt)
#         # close database connection
#         ibm_db.close(db2conn)
    
#     end = time.time()
#     elapse = end - start
#     return render_template('largest_around_place.html', ci=ans, elapse=elapse)



port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
