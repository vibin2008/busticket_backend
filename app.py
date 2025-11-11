from flask import Flask,request,jsonify,redirect,render_template,session
import mysql.connector as mysql
from flask_cors import CORS
import requests
import uuid
from urllib.parse import quote
from dotenv import load_dotenv
import os
import time


con = mysql.connect(host="sql7.freesqldatabase.com",user="sql7806840",passwd="HZS5YNagP3",database="sql7806840")
cur = con.cursor()


def data(a):
    stop = []
    dis = []
    query = f"select * from {a}"
    cur.execute(query)
    try:
        while True:
            dat = cur.fetchone()
            stop.append(dat[0])
            dis.append(dat[1])
    except:
        pass
    return stop,dis

def payment(price,frm,to):
    global APP_ID
    global SECRET_KEY
    load_dotenv('.env') 
    APP_ID = os.getenv('api')
    SECRET_KEY = os.getenv('secret')
    
    encoded_from = quote(frm)
    encoded_to = quote(to)
    encoded_price = quote(str(price))

    return_url = f"https://ayla-ropier-consuela.ngrok-free.dev/tick?from={encoded_from}&to={encoded_to}&price={encoded_price}"

    

    url = "https://test.cashfree.com/api/v1/order/create"

    order_id = f"bus_ticket_{uuid.uuid4().hex[:8]}"

    payload = {
    "appId": APP_ID,
    "secretKey": SECRET_KEY,
    "orderId": order_id,
    "orderAmount": price,
    "orderCurrency": "INR",
    "customerName": "Suhas",
    "customerEmail": "suhas@g.cashfree.com",
    "returnUrl": return_url,
    "notifyUrl": "https://ayla-ropier-consuela.ngrok-free.dev/status",
    "customerPhone": "9999999991"
}

    response = requests.request("POST", url, data=payload)

    return response.json()

def checkstatus(order_id):
    global APP_ID
    global SECRET_KEY
    load_dotenv('.env')
    APP_ID = os.getenv('api')
    SECRET_KEY = os.getenv('secret')
    
    url = "https://test.cashfree.com/api/v1/order/info/status"

    payload = {
        "appId": APP_ID,
        "secretKey": SECRET_KEY,
        "orderId": order_id
    }

    response = requests.post(url, data=payload)
    return response.json()


app = Flask(__name__)
app.secret_key = 'vibin'
CORS(app)
dic={}

@app.route('/stop',methods=['POST'])       
def hello(): 
    dic.clear()
    req = request.get_json()
    table_name = req.get("table")
    stop,dis = data(table_name)
    return jsonify({"distance":dis,"stops":stop})

@app.route('/pay',methods=['POST'])
def pay():
    req = request.get_json()
    price = req.get("price")
    frm = req.get("from")
    to = req.get("to")
    response = payment(price,frm,to)
    payment_link = response.get("paymentLink")
    return jsonify({"url":payment_link})

@app.route('/tick', methods=['GET', 'POST'])
def tick():
    if not request.args.get("txStatus"):
        url = request.url
        if "txStatus" not in dic:
            return redirect(f"{url}&txStatus=failed&txTime=none")
        else:
            return redirect(f"{url}&txStatus={dic['txStatus']}&txTime={dic['txTime']}")
        
    else:
        f = request.args.get("from")
        t = request.args.get("to")
        p = request.args.get("price")
        s = request.args.get("txStatus")
        ti = request.args.get("txTime")
        return render_template("index.html", txStatus=s,frm=f,to=t,txTime=ti,price=p)


@app.route('/status',methods=['GET','POST'])
def status():
    data = request.get_json() or request.form.to_dict() or request.args.to_dict()
    order_id = (data.get("data", {}).get("order", {}).get("order_id") or 
                   data.get("orderId") or 
                   data.get("order_id"))
    response = checkstatus(order_id)
    print(response)
    if response and "txStatus" in response:
        dic["txStatus"] = response["txStatus"]
        dic["txTime"] = response.get("txTime", None)
        return jsonify({"message": "Status updated", "data": dic})
    else:
        dic["txStatus"] = "failed"
        dic["txTime"] = None
        return jsonify({"message": "Status updated", "data": dic})


  
if __name__=='__main__': 
   app.run(debug=True)