# CSE-6331 Cloud Computing

## Demo Endpoint

1. IBM Cloud: http://zzy824.us-south.cf.appdomain.cloud/
2. Google App Engine: http://myresearch.uc.r.appspot.com/**(deprecated)**


## Setup Environment your own environment

- For Local Test

``` sh
pip install -r requirements.txt
cd hw1 && python main.py
```

- For deployment

1. IBM Cloud: make sure you have configured database(db2) before hand.

``` sh
git clone https://github.com/824zzy/CSE6331_CloudComputing.git
cd hw1
cf login
cf push
```

2. Google Cloud Platform: make sure your app engine is `Flex` rather than Standard

``` sh
git clone https://github.com/824zzy/CSE6331_CloudComputing.git
cd hw1 && google app deploy
```

## Screen Shots

### Homework1

1. Home Page

<center>
<img src="img/hw1_1.png" width="400" height="400"/> <br>
</center>

2. Display items

<center>
<img src="img/hw1_2.png" width="600" height="400" /> <br>
</center>

3. API: Search & Add

<center>
<img src="img/hw1_3.png" width="400" height="400" /> <br>
</center>

4. API: Remove & Change

<center>
<img src="img/hw1_4.png" width="400" height="400" />
</center>

### Homework2

## About Author

- Name: Zhengyuan Zhu
- StuId: 1001778274
