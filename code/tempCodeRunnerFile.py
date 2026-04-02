from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from pymongo import MongoClient

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
from pymongo import MongoClient

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('../my-Website', 'index.html')

model = joblib.load("../model.pkl")
accuracy = joblib.load("../accuracy.pkl")

client = MongoClient("mongodb://localhost:27017/")
db = client["captchaDB"]
users = db["users"]

TP=TN=FP=FN=0

@app.route("/verify", methods=["POST"])
def verify():

    global TP,TN,FP,FN

    data = request.json

    username=data.get("username")
    password=data.get("password")
    captcha_answer=data.get("captcha_answer")
    user_input=data.get("user_input")
    question=data.get("question")

    mouse=data.get("mouse",0)
    clicks=data.get("clicks",0)
    keys=data.get("keys",0)
    time_spent=data.get("time",0)

    prediction=model.predict([[mouse,clicks,keys,time_spent]])[0]

    user=users.find_one({"username":username,"password":password})
    login_status="Success" if user else "Fail"

    captcha_status="Correct" if captcha_answer==user_input else "Wrong"

    print("\n=== CAPTCHA AUTH ATTEMPT ===")
    print(f"QUESTION: {question}")
    print(f"CAPTCHA ANSWER: {captcha_answer}")
    print(f"USER INPUT: {user_input}")
    print(f"Mouse: {mouse}")
    print(f"Clicks: {clicks}")
    print(f"Keys: {keys}")
    print(f"Time: {time_spent}")
    print(f"CLASSIFICATION: {prediction}")
    print(f"MODEL ACCURACY: {round(accuracy*100,2)}%")
    print(f"LOGIN STATUS: {login_status}")
    print("CAPTCHA TYPE: perception-based")

    if prediction=="bot":
        return jsonify({"status":"Bot detected ❌"})

    if login_status=="Fail":
        return jsonify({"status":"Invalid login ❌"})

    if captcha_status=="Wrong":
        return jsonify({"status":"Wrong CAPTCHA ❌"})

    return jsonify({"status":"Access Granted ✅"})

if __name__ == "__main__":
    app.run(debug=True)