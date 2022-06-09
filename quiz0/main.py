import os
from flask import Flask, render_template, request, url_for, abort, redirect
from flask_cloudy import Storage

import pandas as pd
import math

port = int(os.getenv('PORT', 8800))
curr_file = None

app = Flask(__name__)
app.config.update({
    "STORAGE_PROVIDER": "LOCAL", # Can also be S3, GOOGLE_STORAGE, etc... 
    "STORAGE_KEY": "",
    "STORAGE_SECRET": "",
    "STORAGE_CONTAINER": "./files",  # a directory path for local, bucket name of cloud
    "STORAGE_SERVER": True,
    "STORAGE_SERVER_URL": "/files" # The url endpoint to access files on LOCAL provider
})
# Setup storage
storage = Storage()
storage.init_app(app) 

@app.route("/")
def index():
    csv_obj, other_obj = [], []
    for obj in storage:
        fname = obj.name
        if fname.split('.')[-1]=='csv':
            csv_obj.append(obj)
        else:
            other_obj.append(obj)
    return render_template("index.html", csv_obj=csv_obj, other_obj=other_obj)



@app.route("/view/<path:object_name>")
def view(object_name):
    obj = storage.get(object_name)
    f_type = obj.name.split('.')[-1]
    
    if f_type=='csv':
        df = pd.read_csv('.'+obj.url, engine='python')
        global curr_file
        curr_file = '.'+obj.url
        img_list = df['Picture'].values.tolist()
        names = df['Name'].values.tolist()
        img_urls = ['./files/'+u for u in img_list if isinstance(u, str)]
        info = df.values.tolist()
    elif f_type=='jpg':
        info, img_urls, names = None, None, None
    else:
        info, img_urls, names = None, None, None
        
    return render_template("view.html", obj=obj, info=info, img_urls=img_urls, names=names)



@app.route("/upload", methods=["POST"])
def upload():
    usr_file = request.files.get("file")
    my_object = storage.upload(usr_file)
    return redirect(url_for("view", object_name=my_object.name))



@app.route("/people_by_grade", methods=['POST'])
def search_people_by_grade():
    low = request.form['low_grade']
    high = request.form['high_grade']
    df = pd.read_csv(curr_file, engine='python')
    resp = []
    for _, line in df.iterrows():
        if line[1] != ' ' and not math.isnan(float(line[1])):
            if int(low)<=int(line[1])<=int(high):
                if isinstance(line[4], str):
                    resp.append([line[0], './files/'+line[4], line[3]])
    
    return render_template("people_by_grade.html", grade_resp=resp)



@app.route("/people_by_height", methods=['POST'])
def search_people_by_height():
    height_number = int(float(request.form['height_number']))
    # print('daad', room_number, type(room_number))
    df = pd.read_csv(curr_file, engine='python')
    resp = []
    for _, line in df.iterrows():
        if not math.isnan(line[1]):
            if int(line[1])==int(height_number):
                if isinstance(line[3], str):
                    resp.append([line[0], './files/'+line[3]])
                    
    return render_template("people_by_height.html", people=resp)



@app.route("/change_info", methods=['POST'])
def change_people_info():
    ppl = request.form['change_people']
    area = request.form['change_area']
    val = request.form['target_value']
    
    df = pd.read_csv(curr_file, engine='python')
    df.at[df['Name']==ppl, area] = int(val)
    info = df.values.tolist()
    df.to_csv(curr_file, index=False)
    
    img_url = './files/'+ ppl + '.jpg'
    return render_template("change_info.html", info=info, img_url=img_url)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
