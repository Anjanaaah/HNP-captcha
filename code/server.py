from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
from pymongo import MongoClient
import os

# 🔥 Color terminal
from colorama import Fore, init
init(autoreset=True)

app = Flask(__name__)
CORS(app)

# 🔹 Serve frontend
@app.route('/')
def home():
    return send_from_directory('../my-Website', 'index.html')

# 🔹 Load model
model = joblib.load("model.pkl")
accuracy = joblib.load("accuracy.pkl")

# 🔹 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["captchadb"]
users = db["users"]

# 🔹 Retry tracking
attempts = {}
MAX_ATTEMPTS = 3

# 🔥 VERIFY ROUTE
@app.route("/verify", methods=["POST"])
def verify():

    data = request.json

    username = data.get("username","").strip()
    password = data.get("password","").strip()

    # ✅ Initialize attempts
    if username not in attempts:
        attempts[username] = 0

    captcha_answer = data.get("captcha_answer","")
    user_input = data.get("user_input","")
    question = data.get("question","")

    mouse = data.get("mouse",0)
    clicks = data.get("clicks",0)
    keys = data.get("keys",0)
    time_spent = data.get("time",0)

    # 🔹 ML Prediction
    prediction = model.predict([[mouse,clicks,keys,time_spent]])[0]

    # 🔹 Human Score
    try:
        prob = model.predict_proba([[mouse,clicks,keys,time_spent]])[0]
        human_score = round(prob[1]*100,2)
    except:
        human_score = 0

    # 🔥 BEHAVIOUR-BASED DIFFICULTY
    if human_score > 80:
        difficulty = "Easy"
    elif human_score > 50:
        difficulty = "Medium"
    else:
        difficulty = "Hard"

    # 🔹 DB Check
    user = users.find_one({
        "username": username,
        "password": password
    })

    login_status = "Success" if user else "Fail"

    captcha_status = "Correct" if captcha_answer.strip().lower() == user_input.strip().lower() else "Wrong"

    # 🔥 TERMINAL OUTPUT
    print(Fore.CYAN + "\n=== CAPTCHA AUTH ATTEMPT ===")

    print(Fore.YELLOW + f"USERNAME: {username}")
    print(Fore.YELLOW + f"PASSWORD: {password}")

    print(Fore.YELLOW + f"QUESTION: {question}")
    print(Fore.YELLOW + f"CAPTCHA ANSWER: {captcha_answer}")
    print(Fore.YELLOW + f"USER INPUT: {user_input}")

    print(Fore.CYAN + f"Mouse: {mouse}")
    print(Fore.CYAN + f"Clicks: {clicks}")
    print(Fore.CYAN + f"Keystrokes: {keys}")
    print(Fore.CYAN + f"Time: {time_spent}")

    print(Fore.GREEN + f"HUMAN SCORE: {human_score}%")

    if prediction == "bot":
        print(Fore.RED + "CLASSIFICATION: BOT ❌")
    else:
        print(Fore.GREEN + "CLASSIFICATION: HUMAN ✅")

    print(Fore.MAGENTA + f"CAPTCHA TYPE: text-image")
    print(Fore.BLUE + f"DIFFICULTY LEVEL: {difficulty}")

    # 🔹 Decision Logic

    # ❌ BOT
    if prediction == "bot":
        print(Fore.RED + "⚠️ BOT DETECTED")
        print(Fore.WHITE + "=================================\n")
        return jsonify({
            "status":"Bot detected ❌",
            "difficulty": difficulty,
            "human_score": human_score
        })

    # ❌ LOGIN FAIL
    if login_status == "Fail":
        print(Fore.RED + "❌ INVALID LOGIN")
        print(Fore.WHITE + "=================================\n")
        return jsonify({
            "status":"Invalid login ❌",
            "difficulty": difficulty
        })

    # ❌ CAPTCHA WRONG
    if captcha_status == "Wrong":
        attempts[username] += 1

        print(Fore.RED + f"Wrong CAPTCHA ❌ Attempt {attempts[username]}/{MAX_ATTEMPTS}")

        if attempts[username] >= MAX_ATTEMPTS:
            print(Fore.RED + "⚠️ BLOCKED after max attempts")
            print(Fore.WHITE + "=================================\n")
            return jsonify({
                "status":"Blocked after multiple attempts ❌",
                "difficulty": difficulty
            })

        print(Fore.YELLOW + f"Retry attempt {attempts[username]}")
        print(Fore.WHITE + "=================================\n")

        return jsonify({
            "status": f"Wrong CAPTCHA ❌ (Attempt {attempts[username]}/{MAX_ATTEMPTS})",
            "retry": True,
            "difficulty": difficulty,
            "human_score": human_score
        })

    # ✅ SUCCESS
    attempts[username] = 0

    print(Fore.GREEN + "✅ ACCESS GRANTED")
    print(Fore.WHITE + "=================================\n")

    return jsonify({
        "status":"Access Granted ✅",
        "difficulty": difficulty,
        "human_score": human_score
    })

# 🔹 RUN
if __name__ == "__main__":
    app.run(debug=True)