import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
# import ibm_db
import pymysql
import geocoder
import geopy.distance
from config import *
import time
import pandas as pd

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

@app.route('/')
def index():
   return render_template('index.html', app=appenv)



@app.route('/search_n', methods=['GET'])
def search_n():
    n = int(request.args.get('n'))
    names = str(request.args.get('names'))
    fnames = names.split(',', n)
    print(fnames)
    rows = {}
    # tmp = []
    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))
    i = 0
    for fname in  fnames:
        fname1 = "'" + fname + "'"
        sql = "SELECT COUNT(*) from fruit WHERE name = " + fname1
        cursor = db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)
        rows[str(fname)] = results[0][0]
        i = i + 1

    print(rows)
    return render_template('search_around_place.html', ci=rows)


# @app.route('/search_around_place', methods=['GET'])
# def search_around_place():
#     pop_start = float(request.args.get('start'))*100000
#     pop_end = float(request.args.get('end'))*100000
#     year = request.args.get('year')
#     rows = {}
#     print(pop_start, pop_end, year)
#
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         sql = "SELECT * FROM SP4"
#         stmt = ibm_db.exec_immediate(db2conn, sql)
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             for k, v in result.items():
#                 if k!='STATE' and float(k[1:])==float(year):
#                     if float(pop_start)<float(v)<float(pop_end):
#                         rows[result["STATE"]] = result[k]
#             result = ibm_db.fetch_assoc(stmt)
#         # close database connection
#         ibm_db.close(db2conn)
#     return render_template('search_around_place.html', ci=rows)



@app.route('/search_scale', methods=['GET'])
def search_scale():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    print(start, end)
    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        print('数据库连接成功!')
    except pymysql.Error as e:
        print('数据库连接失败' + str(e))

    sql = "SELECT * from fruit WHERE number < " + str(end) + " AND number > " + str(start)
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    print(results)
    scatter_attr = []
    for result in results:
        scatter_attr.append({"X": float(result[1]), "Y": float(result[2])})

    print('zzzz', scatter_attr)
    return render_template('search_scale.html', sa=scatter_attr)


port = os.getenv('PORT', '5001')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

""" Ref
1. [D3v5 map example](http://bl.ocks.org/almccon/1bcde7452450c153d8a0684085f249fd)
2. [Interactive Bar Chart Pie Chart](http://bl.ocks.org/cflavs/695d3215ccbce135d3bd)
"""