from flask import Flask,redirect,render_template,request, jsonify
import re
from functools import reduce

# EB looks for an 'application' callable by default.
application = Flask(__name__)


@application.route('/')
def index():
   return render_template('index.html')
 
 
@application.route('/_calculate')
def calculate():
    a = request.args.get('number1', '0')
    operator = request.args.get('operator', '+')
    b = request.args.get('number2', '0')
    # validate the input data
    m = re.match(r'^\-?\d*[.]?\d*$', a)
    n = re.match(r'^\-?\d*[.]?\d*$', b)
    print(a, b, m, n, operator)
    # if m is None or n is None or operator not in '+-*/!%':
    #     return jsonify(result='Error!')
    
    if operator == '/':
        if b==0:
            jsonify(result='Can not divide 0')
        else:
            result = eval(a + operator + str(float(b)))
    elif operator == '!':
        
        result = reduce(lambda x,y: x*y, range(1,int(a)+1))
    else:
        result = eval(a + operator + b)
    return jsonify(result=result)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()