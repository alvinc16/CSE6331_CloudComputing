import os

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
     "port": 8080,
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