# CSE-6331 Cloud Computing

## Demo Endpoint

1. IBM Cloud: http://zzy824.us-south.cf.appdomain.cloud/
2. Azure: http://zzy824-quake.azurewebsites.net
3. Google App Engine: http://myresearch.uc.r.appspot.com/ **(deprecated)**

## Setup Environment

### Trouble Shooting

You may need to export environment variable: `export DYLD_LIBRARY_PATH=[your path to python]/site-packages/clidriver/lib:$DYLD_LIBRARY_PATH`

### Local Test

``` sh
pip install -r requirements.txt
cd [hw*] && python [main/application/...].py
```

### For deployment

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

3. Microsoft Azure
``` sh
git clone https://github.com/824zzy/CSE6331_CloudComputing.git
# login your azure account through azure client
cd hw1 && az webapp up --sku F1 -n [your app name]
```

## Screen Shots

- [Homework 1: Upload Files and Display Data](hw1/README.md)
- [Homework 2: Connect to Database and Fancy Query](hw2/README.md)
- [Homework 3: Accelerate IDSU[insert/delete/select/update] by Memcache](hw3/README.md)
- [Homework 4: Visualization by D3.js](hw4/README.md)
- [Homework 5: TODO:](hw5/README.md)
- [Homework 6: TODO:](hw6/README.md)

## About Author

- Name: Zhengyuan Zhu
- StuId: 1001778274
