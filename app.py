from flask import Flask,request,jsonify,redirect
import mysql.connector as mysql
from flask_cors import CORS
import requests
import uuid
from dotenv import load_dotenv
import os


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

def payment(price):
    global APP_ID
    global SECRET_KEY
    load_dotenv('.ev') 
    APP_ID = os.getenv('api')
    SECRET_KEY = os.getenv('secret')
    print(APP_ID,SECRET_KEY)
    # APP_ID,SECRET_KEY = id()
    

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
    "notifyUrl": "https://ayla-ropier-consuela.ngrok-free.dev/status",
    "returnUrl": "https://ayla-ropier-consuela.ngrok-free.dev/status",
    "customerPhone": "9999999991"
}

    response = requests.request("POST", url, data=payload)

    return response.json()

def checkstatus(order_id):
    global APP_ID
    global SECRET_KEY
    # Ensure env vars are loaded
    if not APP_ID or not SECRET_KEY:
        load_dotenv('.ev')
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
CORS(app)
@app.route('/stop',methods=['POST'])       
def hello(): 
    req = request.get_json()
    table_name = req.get("table")
    stop,dis = data(table_name)
    return jsonify({"distance":dis,"stops":stop})

@app.route('/pay',methods=['POST'])
def pay():
    req = request.get_json()
    price = req.get("price")
    response = payment(price)
    payment_link = response.get("paymentLink")
    return jsonify({"url":payment_link})

@app.route('/status',methods=['POST','GET'])
def status():
    data = request.get_json() or request.form.to_dict()
    order_id = data.get("data", {}).get("order", {}).get("order_id")
    response = checkstatus(order_id)
    print(response)
    if response['orderStatus'] == "PAID":
        return redirect("https://ticketboking.netlify.app?status=paid")
    return redirect("https://ticketboking.netlify.app?status=notpaid")


  
if __name__=='__main__': 
   app.run(debug=True)