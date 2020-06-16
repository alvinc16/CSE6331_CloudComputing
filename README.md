# CSE-6331 Cloud Computing

## Demo Endpoint

1. Google App Engine: http://myresearch.uc.r.appspot.com/**(deprecated)**
2. IBM Cloud: http://zzy824.us-south.cf.appdomain.cloud/

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

<img src="img/hw1_1.png" width="400" height="400" /> <br>

2. Display items

<img src="img/hw1_2.png" width="600" height="400" /> <br>

3. API: Search & Add

<img src="img/hw1_3.png" width="400" height="400" /> <br>

4. API: Remove & Change

<img src="img/hw1_4.png" width="400" height="400" />

### Homework2

## About Author

- Name: Zhengyuan Zhu
- StuId: 1001778274
