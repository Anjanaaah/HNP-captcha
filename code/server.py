from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
from pymongo import MongoClient
from colorama import Fore, init
import os
import math


# =========================================================
# INITIALIZATION
# =========================================================

init(autoreset=True)

app = Flask(__name__)
CORS(app)


# =========================================================
# FRONTEND
# =========================================================

@app.route("/")
def home():

    return send_from_directory(
        "../my-Website",
        "index.html"
    )


# =========================================================
# LOAD ML MODEL
# =========================================================

model = joblib.load("model.pkl")
accuracy = joblib.load("accuracy.pkl")

print(Fore.GREEN + "✅ ML model loaded")


# =========================================================
# MONGODB
# =========================================================

client = MongoClient(
    "mongodb://localhost:27017/"
)

db = client["captchadb"]

users = db["users"]


# =========================================================
# ATTEMPT TRACKING
# =========================================================

attempts = {}

MAX_ATTEMPTS = 3


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


def safe_int(value):
    try:
        return int(value)
    except:
        return 0


# =========================================================
# VERIFY
# =========================================================

@app.route(
    "/verify",
    methods=["POST"]
)
def verify():

    data = request.json or {}


    # =====================================================
    # BASIC DATA
    # =====================================================

    username = str(
        data.get("username", "")
    ).strip()

    password = str(
        data.get("password", "")
    ).strip()

    captcha_answer = str(
        data.get("captcha_answer", "")
    )

    user_input = str(
        data.get("user_input", "")
    )

    question = str(
        data.get("question", "")
    )


    # =====================================================
    # ORIGINAL ML FEATURES
    # =====================================================

    mouse = safe_int(
        data.get("mouse", 0)
    )

    clicks = safe_int(
        data.get("clicks", 0)
    )

    keys = safe_int(
        data.get("keys", 0)
    )

    time_spent = safe_int(
        data.get("time", 0)
    )


    # =====================================================
    # ADDITIONAL BEHAVIOURAL FEATURES
    # =====================================================

    mouse_distance = safe_float(
        data.get(
            "mouse_distance",
            0
        )
    )

    direction_changes = safe_int(
        data.get(
            "direction_changes",
            0
        )
    )

    average_speed = safe_float(
        data.get(
            "average_speed",
            0
        )
    )

    average_mouse_interval = safe_float(
        data.get(
            "average_mouse_interval",
            0
        )
    )

    average_click_interval = safe_float(
        data.get(
            "average_click_interval",
            0
        )
    )

    average_key_interval = safe_float(
        data.get(
            "average_key_interval",
            0
        )
    )

    key_interval_variance = safe_float(
        data.get(
            "key_interval_variance",
            0
        )
    )


    # =====================================================
    # DEBUG BEHAVIOUR
    # =====================================================

    print(
        Fore.CYAN +
        "\n========== BEHAVIOUR DATA =========="
    )

    print(
        Fore.YELLOW +
        f"Mouse movements: {mouse}"
    )

    print(
        Fore.YELLOW +
        f"Mouse distance: {mouse_distance:.2f}"
    )

    print(
        Fore.YELLOW +
        f"Direction changes: {direction_changes}"
    )

    print(
        Fore.YELLOW +
        f"Clicks: {clicks}"
    )

    print(
        Fore.YELLOW +
        f"Keystrokes: {keys}"
    )

    print(
        Fore.YELLOW +
        f"Time: {time_spent} ms"
    )

    print(
        Fore.YELLOW +
        f"Average speed: {average_speed:.2f}"
    )

    print(
        Fore.YELLOW +
        f"Average key interval: {average_key_interval:.2f}"
    )

    print(
        Fore.YELLOW +
        f"Key interval variance: {key_interval_variance:.2f}"
    )


    # =====================================================
    # ML PREDICTION
    # =====================================================

    features = [[
        mouse,
        clicks,
        keys,
        time_spent
    ]]

    try:

        prediction = model.predict(
            features
        )[0]

    except Exception as e:

        print(
            Fore.RED +
            f"Prediction error: {e}"
        )

        return jsonify({
            "status":
                "ML prediction failed ❌"
        })


    # =====================================================
    # HUMAN SCORE
    # =====================================================

    try:

        prob = model.predict_proba(features)[0]

        classes = list(model.classes_)

        print(
            Fore.CYAN +
            f"Model classes: {classes}"
        )


        # Find HUMAN class safely
        human_index = None

        for i, cls in enumerate(classes):

            if str(cls).lower() == "human":

                human_index = i
                break


        if human_index is not None:

            human_score = round(
                prob[human_index] * 100,
                2
            )

        else:

            # If model uses 0/1 labels,
            # don't blindly assume prob[1].
            human_score = round(
                max(prob) * 100,
                2
            )


    except Exception as e:

        print(
            Fore.RED +
            f"Probability error: {e}"
        )

        human_score = 0


    # =====================================================
    # DIFFICULTY
    # =====================================================

    if human_score > 80:

        difficulty = "Easy"

    elif human_score > 50:

        difficulty = "Medium"

    else:

        difficulty = "Hard"


    # =====================================================
    # DATABASE CHECK
    # =====================================================

    user = users.find_one({

        "username":
            username,

        "password":
            password

    })

    login_status = (
        "Success"
        if user
        else "Fail"
    )


    # =====================================================
    # CAPTCHA CHECK
    # =====================================================

    captcha_status = (

        "Correct"

        if captcha_answer.strip().lower()
        ==
        user_input.strip().lower()

        else "Wrong"
    )


    # =====================================================
    # TERMINAL OUTPUT
    # =====================================================

    print(
        Fore.CYAN +
        "\n=== CAPTCHA AUTH ATTEMPT ==="
    )

    print(
        Fore.YELLOW +
        f"USERNAME: {username}"
    )

    print(
        Fore.YELLOW +
        f"QUESTION: {question}"
    )

    print(
        Fore.YELLOW +
        f"CAPTCHA ANSWER: {captcha_answer}"
    )

    print(
        Fore.YELLOW +
        f"USER INPUT: {user_input}"
    )

    print(
        Fore.CYAN +
        f"Mouse: {mouse}"
    )

    print(
        Fore.CYAN +
        f"Clicks: {clicks}"
    )

    print(
        Fore.CYAN +
        f"Keystrokes: {keys}"
    )

    print(
        Fore.CYAN +
        f"Time: {time_spent}"
    )

    print(
        Fore.CYAN +
        f"Mouse distance: {mouse_distance:.2f}"
    )

    print(
        Fore.CYAN +
        f"Direction changes: {direction_changes}"
    )

    print(
        Fore.GREEN +
        f"HUMAN SCORE: {human_score}%"
    )

    print(
        Fore.MAGENTA +
        "CAPTCHA TYPE: text-image"
    )

    print(
        Fore.BLUE +
        f"DIFFICULTY LEVEL: {difficulty}"
    )

    print(
        Fore.WHITE +
        f"MODEL PREDICTION: {prediction}"
    )


    # =====================================================
    # BOT DETECTION
    # =====================================================

    if str(prediction).lower() == "bot":

        print(
            Fore.RED +
            "⚠️ BOT DETECTED"
        )

        print(
            Fore.WHITE +
            "=================================\n"
        )

        return jsonify({

            "status":
                "Bot detected ❌",

            "difficulty":
                difficulty,

            "human_score":
                human_score

        })


    # =====================================================
    # CAPTCHA FIRST
    # =====================================================

    if captcha_status == "Wrong":

        if username not in attempts:

            attempts[username] = 0

        attempts[username] += 1

        print(
            Fore.RED +
            f"Wrong CAPTCHA ❌ "
            f"Attempt "
            f"{attempts[username]}/"
            f"{MAX_ATTEMPTS}"
        )


        if attempts[username] >= MAX_ATTEMPTS:

            print(
                Fore.RED +
                "⚠️ BLOCKED after max attempts"
            )

            print(
                Fore.WHITE +
                "=================================\n"
            )

            return jsonify({

                "status":
                    "Blocked after multiple attempts ❌",

                "difficulty":
                    difficulty,

                "human_score":
                    human_score

            })


        return jsonify({

            "status":
                f"Wrong CAPTCHA ❌ "
                f"(Attempt "
                f"{attempts[username]}/"
                f"{MAX_ATTEMPTS})",

            "retry":
                True,

            "difficulty":
                difficulty,

            "human_score":
                human_score

        })


    # =====================================================
    # LOGIN FAILURE
    # =====================================================

    if login_status == "Fail":

        print(
            Fore.RED +
            "❌ INVALID LOGIN"
        )

        print(
            Fore.WHITE +
            "=================================\n"
        )

        return jsonify({

            "status":
                "Invalid login ❌",

            "difficulty":
                difficulty,

            "human_score":
                human_score

        })


    # =====================================================
    # SUCCESS
    # =====================================================

    attempts[username] = 0

    print(
        Fore.GREEN +
        "✅ ACCESS GRANTED"
    )

    print(
        Fore.WHITE +
        "=================================\n"
    )


    return jsonify({

        "status":
            "Access Granted ✅",

        "difficulty":
            difficulty,

        "human_score":
            human_score

    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )
