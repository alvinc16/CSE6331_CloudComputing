import os
from flask import Flask, render_template, request, url_for, abort, redirect
from flask_cloudy import Storage

import pandas as pd
import math

port = int(os.getenv('PORT', 5000))
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



@app.route("/people_by_id", methods=['POST'])
def search_people_by_id():
    stu_id = request.form['stu_id']
    df = pd.read_csv(curr_file, engine='python')
    resp = []
    for _, line in df.iterrows():
        if line[1] != ' ' and not math.isnan(float(line[1])):
            if stu_id == line[1]:
                if isinstance(line[4], str):
                    resp.append([line[0], './files/'+line[4], line[5]])
    
    return render_template("people_by_id.html", grade_resp=resp)


@app.route("/people_by_range", methods=['POST'])
def search_people_by_range():
    low = request.form['low_num']
    high = request.form['high_num']
    df = pd.read_csv(curr_file, engine='python')
    resp = []
    for _, line in df.iterrows():
        if line[1] != ' ' and not math.isnan(float(line[1])):
            if int(low) <= int(line[1]) <= int(high):
                if isinstance(line[2], str):
                    print(line[0])
                    resp.append([line[0], line[1], '../files/' + line[2], line[3]])
    return render_template("people_by_range.html", people=resp)

@app.route("/people_by_name", methods=['POST'])
def search_people_by_name():
    img_name = request.form['img_name']
    print('zzz', img_name)
    df = pd.read_csv(curr_file, engine='python')
    resp = []
    for _, line in df.iterrows():
        print('zzz', line[0])
        if line[0] and isinstance(line[0], str):
            if line[0]==img_name:
                resp.append([line[0], '../files/' + line[2]])
                    
    return render_template("people_by_img.html", people=resp)



@app.route("/change_info", methods=['POST'])
def change_people_info():
    ppl = request.form['change_people']
    val = request.form['target_value']
    pic = request.form['picture_value']
    print(val)
    df = pd.read_csv(curr_file, engine='python')

    for index, line in df.iterrows():
        if line[0] == ppl:
            if val != '':
                df['Keywords'][index] = val
            if pic != '':
                df['Picture'][index] = pic
    info = df.values.tolist()
    df.to_csv(curr_file, index=False)
    try:
        img_url = './files/'+ df[df['Name']==ppl].Picture.values[0]
    except:
        img_url = ''
    
    return render_template("change_info.html", info=info, img_url=img_url)


@app.route("/add_info", methods=['POST'])
def add_people_info():
    name = request.form['name']
    num = request.form['num']
    key = request.form['key']
    df = pd.read_csv(curr_file, engine='python')
    df.loc[1] = [name, num, '../files/a.jpg', key]
    info = df.values.tolist()
    df.to_csv(curr_file, index=False)
    img_url = ''

    return render_template("change_info.html", info=info, img_url=img_url)

@app.route("/rm_info", methods=['POST'])
def rm_people_info():
    name = request.form['name']
    df = pd.read_csv(curr_file, engine='python')
    for index, line in df.iterrows():
        if line[0] == name:
            print(index)
            df.drop(index=index)
    info = df.values.tolist()
    df.to_csv(curr_file, index=False)
    img_url = ''

    return render_template("change_info.html", info=info, img_url=img_url)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
