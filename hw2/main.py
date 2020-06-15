import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
import ibm_db
import geocoder
import geopy.distance

app = Flask(__name__)
os.environ['VCAP_SERVICES'] = """{
  "dashDB For Transactions": [
   {
    "binding_name": null,
    "credentials": {
     "db": "BLUDB",
     "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=xlq47970;PWD=0q2bqjtqq21lf@97;",
     "host": "dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net",
     "hostname": "dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net",
     "https_url": "https://dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net",
     "jdbcurl": "jdbc:db2://dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
     "parameters": {
      "role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager"
     },
     "password": "0q2bqjtqq21lf@97",
     "port": 50000,
     "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=xlq47970;PWD=0q2bqjtqq21lf@97;Security=SSL;",
     "ssljdbcurl": "jdbc:db2://dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net:50001/BLUDB:sslConnection=true;",
     "uri": "db2://xlq47970:0q2bqjtqq21lf%4097@dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
     "username": "xlq47970"
    },
    "instance_name": "Db2-ml",
    "label": "dashDB For Transactions",
    "name": "Db2-ml",
    "plan": "Lite",
    "provider": null,
    "syslog_drain_url": null,
    "tags": [
     "big_data",
     "ibm_created",
     "db2",
     "sqldb",
     "purescale",
     "sql",
     "ibm_dedicated_public",
     "db2 on cloud",
     "db2oncloud",
     "dash",
     "dashdb",
     "oracle",
     "database",
     "transactions",
     "flex",
     "dbaas",
     "lite",
     "apidocs_enabled",
     "ibmcloud-alias"
    ],
    "volume_mounts": []
   }
  ]
 }"""
os.environ['VCAP_APPLICATION'] = """{
  "application_id": "ac5a1d40-d5db-4d44-9acc-f5d3b7b9cf9b",
  "application_name": "zzy824",
  "application_uris": [
   "zzy824.us-south.cf.appdomain.cloud"
  ],
  "application_version": "ca66bff6-a924-4d65-89d0-2292c9702e58",
  "cf_api": "https://api.us-south.cf.cloud.ibm.com",
  "limits": {
   "disk": 1024,
   "fds": 16384,
   "mem": 128
  },
  "name": "zzy824",
  "organization_id": "9e924a6d-fcc7-4057-976d-fc08718f2f25",
  "organization_name": "zhuzhengyuan824@gmail.com",
  "process_id": "ac5a1d40-d5db-4d44-9acc-f5d3b7b9cf9b",
  "process_type": "web",
  "space_id": "5d76b9bf-d5fb-44ac-99e7-134c4680c49d",
  "space_name": "dev",
  "uris": [
   "zzy824.us-south.cf.appdomain.cloud"
  ],
  "users": null,
  "version": "ca66bff6-a924-4d65-89d0-2292c9702e58"
}"""
# get service information if on IBM Cloud Platform
if 'VCAP_SERVICES' in os.environ:
    db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB For Transactions'][0]
    db2cred = db2info["credentials"]
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    raise ValueError('Expected cloud environment')

# handle database request and query city information
# def city(name=None):
#     # connect to DB2
#     db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
#     if db2conn:
#         # we have a Db2 connection, query the database
#         sql="select * from cities where name=? order by population desc"
#         # Note that for security reasons we are preparing the statement first,
#         # then bind the form input as value to the statement to replace the
#         # parameter marker.
#         stmt = ibm_db.prepare(db2conn,sql)
#         ibm_db.bind_param(stmt, 1, name)
#         ibm_db.execute(stmt)
#         rows=[]
#         # fetch the result
#         result = ibm_db.fetch_assoc(stmt)
#         while result != False:
#             rows.append(result.copy())
#             result = ibm_db.fetch_assoc(stmt)
#         # close database connection
#         ibm_db.close(db2conn)
#     return render_template('city.html', ci=rows)



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
        # sql="select * from cities where name=? order by population desc"
        sql = "SELECT * FROM EARTHQUAKE ORDER BY MAG DESC FETCH FIRST ? ROWS ONLY;"
        # sql = "SELECT * FROM QUIZ2 ORDER BY MAG DESC FETCH FIRST ? ROWS ONLY;"
        stmt = ibm_db.prepare(db2conn, sql)
        ibm_db.bind_param(stmt, 1, number)
        ibm_db.execute(stmt)
        
        # stmt = ibm_db.exec_immediate(db2conn, sql)
        # ibm_db.bind_param(stmt, 1, name)
        # ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        print(rows)
        ibm_db.close(db2conn)
    return render_template('large_n.html', ci=rows)



@app.route('/search_around_place', methods=['GET'])
def search_around_place():
    distance = request.args.get('distance', 500)
    city = request.args.get('city', 'arlington')
    
    usr_g_json = geocoder.osm(city).json
    trgt_coords = (usr_g_json['lat'], usr_g_json['lng'])

    # connect to DB2
    db2conn = ibm_db.connect(db2cred['ssldsn'], "","")
    if db2conn:
        sql = "SELECT * FROM EARTHQUAKE"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_coords = (result['LATITUDE'], result['LONGTITUDE'])
            if geopy.distance.vincenty(curr_coords, trgt_coords).km<distance:
                rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        # print(rows)
        ibm_db.close(db2conn)
    return render_template('search_around_place.html', ci=rows)



@app.route('/count_scale', methods=['GET'])
def count_scale(start='2020-06-01', end='2020-06-08'):
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
        # stmt = ibm_db.exec_immediate(db2conn, sql)
        stmt = ibm_db.prepare(db2conn, sql)
        ibm_db.bind_param(stmt, 1, scale)
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            curr_date = result['TIME'][:10]
            curr_date = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
            if start<=curr_date<=end:
                rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        # print(rows)
        ibm_db.close(db2conn)
    return render_template('count_scale.html', ci=rows)

@app.route('/search_scale', methods=['GET'])
def search_scale():
    number = request.args.get('number', 1000, type=int)
    today = datetime.date.today()
    ago = today - datetime.timedelta(days=number)
    print(ago)
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
