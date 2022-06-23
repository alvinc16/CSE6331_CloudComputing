import os
import time

from flask import Flask,redirect,render_template,request
import urllib
import pymysql
import datetime
import json
# import ibm_db
import geocoder
import geopy.distance
from config import *

app = Flask(__name__)

DBHOST = 'localhost'
DBUSER = 'root'
DBPASS = '19980604'
DBNAME = 'volcano'

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



# @app.route('/search_largest_n', methods=['GET'])
# def largest_n(number=5):
#     number = 1
#     count = 19757
#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM EARTHQUAKE ORDER BY MAG DESC FETCH FIRST ? ROWS ONLY;"
#         stmt = ibm_db.prepare(db2conn, sql)
#         ibm_db.bind_param(stmt, 1, number)
#         ibm_db.execute(stmt)
#
#         rows=[]
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             rows.append(result.copy())
#             result = ibm_db.fetch_assoc(stmt)
#
#         ibm_db.close(db2conn)
#     return render_template('large_n.html', ci=rows, c=count)




@app.route('/search_around_place', methods=['GET'])
def search_around_place():
    X1 = float(request.args.get('X1'))
    Y1 = float(request.args.get('Y1'))
    X2 = float(request.args.get('X2'))
    Y2 = float(request.args.get('Y2'))
    print(X1,X2,Y1,Y2)
    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))
    print(X1, X2, Y1, Y2)
    sql = "SELECT * FROM earthquake"
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    rows=[]
    for result in results:
        print(result)
        curr_x = float(result[1])
        curr_y = float(result[2])
        if X1<curr_x<X2 or X2<curr_x<X1:
            if Y1<curr_y<Y2 or Y2<curr_y<Y1:
                rows.append(result.copy())
    db.close()
    return render_template('search_around_place.html', ci=rows)


@app.route('/search_around_place_by_nn', methods=['GET'])
def search_around_place_by_nn():
    nn = str(request.args.get('nn'))
    magnitude1 = str(request.args.get('magnitude1'))
    magnitude2 = str(request.args.get('magnitude2'))
    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))
    sql = "SELECT * FROM earthquake WHERE net = " + nn + "and mag <" + magnitude1 + " and mag >" + magnitude2 + " order by mag limit 5"
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    rows = []

    for result in results:
        rows.append(result.copy())
    db.close()
    return render_template('search_around_place.html', ci=rows)

@app.route('/search_around_place_by_day', methods=['GET'])
def search_around_place_by_day():
    Z1 = float(request.args.get('Z1'))
    Z2 = float(request.args.get('Z2'))
    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))

    sql = "SELECT * FROM earthquake WHERE time <"+Z1+"and time >"+Z2
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    rows = []
    for result in results:
        rows.append(result.copy())
    db.close()
    return render_template('search_around_place.html', ci=rows)

@app.route('/update_nn_2_rl', methods=['GET'])
def update_nn_2_rl():
    nn = float(request.args.get('nn'))
    rl = float(request.args.get('rl'))
    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))
    sql = "UPDATE earthquake SET net = " + rl + "WHERE net = " + nn
    cursor = db.cursor()
    cursor.execute(sql)
    sql = "SEARCH * FROM earthquake limit 100"
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()
    return render_template('search_around_place.html', ci=results)

@app.route('/search_volcano_by_range', methods=['GET'])
def search_volcano_by_range():
    R1 = float(request.args.get('R1'))
    R2 = float(request.args.get('R2'))
    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))
    sql = "SELECT * FROM volcano WHERE number > " + str(int(R1)) + " and number < " + str(int(R2))
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    rows = []
    min = 999999
    max = 0
    for result in results:
        print(result)
        if result[6] > max:
            max = result[6]
        if result[6] < min:
            min = result[6]
        rows.append(result)
    db.close()
    return render_template('search_around_place.html', ci=results, min=min, max=max)

@app.route('/search_volcano_by_seq', methods=['GET'])
def search_volcano_by_seq():
    N1 = int(request.args.get('N1'))
    N2 = int(request.args.get('N2'))
    NN = int(request.args.get('NN'))
    TT = int(request.args.get('TT'))

    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))
    times = []
    for num in range(1, TT+1):
        time_begin = time.time()
        print(time_begin)
        sql1 = "SELECT number FROM vindex WHERE seq > " + str(N1) + " AND seq < " + str(N2)
        sql = "SELECT * FROM volcano WHERE number in ( " + sql1 + ")"
        cursor = db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        time_end = time.time()
        print(time_end)
        times.append(time_end-time_begin)
    rows = []
    i = 0
    for result in results:
        i = i + 1
        print(result)
        rows.append(result)
        if i == NN:
            break
    db.close()
    return render_template('search_volcano_by_seq.html', ci=results, row=rows, times=times)



# @app.route('/count_scale', methods=['GET'])
# def count_scale():
#     start = request.args.get('start', default='2020-06-01')
#     end = request.args.get('end', default='2020-06-01')
#     start = '2020-06-01' if start=='' else start
#     end = '2020-06-08' if end=='' else end
#     start = datetime.datetime.strptime(start, "%Y-%m-%d")
#     end = datetime.datetime.strptime(end, "%Y-%m-%d")
#     scale = request.args.get('scale', '3')
#
#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM EARTHQUAKE WHERE MAGTYPE=\'ml\' AND MAG>=?"
#         stmt = ibm_db.prepare(db2conn, sql)
#         ibm_db.bind_param(stmt, 1, scale)
#         ibm_db.execute(stmt)
#
#         rows=[]
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             curr_date = result['TIME'][:10]
#             curr_date = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
#             if start<=curr_date<=end:
#                 rows.append(result.copy())
#             result = ibm_db.fetch_assoc(stmt)
#
#         ibm_db.close(db2conn)
#     return render_template('count_scale.html', ci=rows)

# @app.route('/search_scale', methods=['GET'])
# def search_scale():
#     low_bound = request.args.get('low_bound', 2, type=int)
#     high_bound = request.args.get('high_bound', 5, type=int)
#     partition = request.args.get('partition', 3, type=int)
#     tmp = low_bound
#     delta = (high_bound-low_bound)/partition
#     slots = []
#     ans = {}
#     ans_max = {}
#     while tmp<high_bound:
#         slots.append([tmp, tmp+delta])
#         tmp += delta
#     for slot in slots:
#         ans[(slot[0], slot[1])] = 0
#         ans_max[(slot[0], slot[1])] = 0
#
#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM QUAKES"
#         stmt = ibm_db.exec_immediate(db2conn, sql)
#         # fetch the result
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             curr_mag = float(result['MAG'])
#             if low_bound<curr_mag<high_bound:
#                 for slot in slots:
#                     if slot[0]<curr_mag<slot[1]:
#                         ans[(slot[0], slot[1])] += 1
#                         if ans_max[(slot[0], slot[1])]==0:
#                             ans_max[(slot[0], slot[1])] = result.copy()
#                         elif curr_mag>float(ans_max[(slot[0], slot[1])]['MAG']):
#                             ans_max[(slot[0], slot[1])] = result.copy()
#
#             result = ibm_db.fetch_assoc(stmt)
#         # close database connection
#         ibm_db.close(db2conn)
#     return render_template('search_scale.html', ci1=ans, ci2=ans_max)



# @app.route('/compare_two_place', methods=['GET'])
# def compare_two_place():
#     distance = request.args.get('distance', 1000, type=int)
#
#     placeA, placeB = request.args.get('placeA'), request.args.get('placeB')
#     placeA = 'Anchorage' if placeA=='' else placeA
#     placeB = 'Dallas' if placeB=='' else placeB
#
#     pA_json, pB_json = geocoder.osm(placeA).json, geocoder.osm(placeB).json
#     trgtA_coords, trgtB_coords = (pA_json['lat'], pA_json['lng']), (pB_json['lat'], pB_json['lng'])
#
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
#     print(len(ansA), len(ansB))
#     return render_template('compare_two_place.html', ciA=ansA, ciB=ansB, pA=placeA, pB=placeB)



# @app.route('/largest_around_place', methods=['GET'])
# def largest_around_place():
#     distance = request.args.get('distance', 500, type=int)
#     city = request.args.get('city')
#     city = 'Dallas' if city=='' else city
#     usr_g_json = geocoder.osm(city).json
#     trgt_coords = (usr_g_json['lat'], usr_g_json['lng'])
#
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
#     return render_template('largest_around_place.html', ci=ans)



port = os.getenv('PORT', '8080')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
