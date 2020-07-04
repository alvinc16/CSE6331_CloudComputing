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
    partition = float(request.args.get('partition'))
    year = float(request.args.get('year'))
    rows = {}
    tmp = []

    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM SP4"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            for k, v in result.items():
                if k!='STATE' and float(k[1:])==float(year):
                    tmp.append(v)
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    maxp, minp = max(tmp), min(tmp)
    step = int((maxp-minp)//partition)
    print(maxp, minp)
    
    for i in range(minp, maxp, step):
        for t in tmp:
            if i<t<i+step:
                if "{}_{}".format(str(i), str((i+step))) not in rows:
                    rows["{}_{}".format(str(i), str((i+step)))] = 1
                else:
                    rows["{}_{}".format(str(i), str((i+step)))] += 1
                    
    return render_template('search_around_place.html', ci=rows)


@app.route('/search_around_place', methods=['GET'])
def search_around_place():
    pop_start = float(request.args.get('start'))*100000
    pop_end = float(request.args.get('end'))*100000
    year = request.args.get('year')
    rows = {}
    print(pop_start, pop_end, year)

    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM SP4"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            for k, v in result.items():
                if k!='STATE' and float(k[1:])==float(year):
                    if float(pop_start)<float(v)<float(pop_end):
                        rows[result["STATE"]] = result[k]
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    return render_template('search_around_place.html', ci=rows)



@app.route('/search_scale', methods=['GET'])
def search_scale():
    state = request.args.get('state')
    start = request.args.get('start')
    end = request.args.get('end')
    print(state, start, end)
    
    # today = datetime.date.today()
    # ago = today - datetime.timedelta(days=number)
    # slot01, slot12, slot23, slot34, slot45, slot56, slot67 = 0, 0, 0, 0, 0, 0, 0
    scatter_attr = []
    
    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM SP4 WHERE STATE=\'{}\'".format(state)
        stmt = ibm_db.exec_immediate(db2conn, sql)
        # fetch the result
        
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            for k, v in result.items():
                if k!='STATE' and float(start)<=float(k[1:])<=float(end):
                        scatter_attr.append({"Year": float(k[1:]), "Population": float(v)})
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    print('zzzz', scatter_attr)
    return render_template('search_scale.html', sa=scatter_attr)


port = os.getenv('PORT', '5001')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

""" Ref
1. [D3v5 map example](http://bl.ocks.org/almccon/1bcde7452450c153d8a0684085f249fd)
2. [Interactive Bar Chart Pie Chart](http://bl.ocks.org/cflavs/695d3215ccbce135d3bd)
"""