# 🔐 Human Neuro-Perception CAPTCHA (HNP-CAPTCHA)

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?logo=mongodb)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-orange?logo=scikitlearn)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![License](https://img.shields.io/badge/License-Educational-blue)

---

📌 Overview

HNP-CAPTCHA is an advanced CAPTCHA system that combines visual perception challenges with behavioral analysis to distinguish humans from bots.
Unlike traditional CAPTCHAs, this system evaluates how users interact (mouse movement, typing speed, clicks) along with solving visual tasks.

---

🚀 Features

- 🧠 Cognitive CAPTCHA
  
  - Questions based on perception (size, position, tilt, blur, etc.)

- 🤖 AI-Based Bot Detection
  
  - Machine Learning model classifies user as Human / Bot

- 🎯 Dynamic Difficulty Adjustment
  
  - Easy → Medium → Hard based on user behavior

- 📊 Behavior Tracking
  
  - Mouse movements
  - Click count
  - Keystrokes
  - Time taken

- 🔐 Secure Login Simulation
  
  - CAPTCHA + Username/Password validation

---

🛠️ Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask)
- Database: MongoDB
- Machine Learning: Scikit-learn

---

⚙️ How It Works

1. User enters login credentials
2. CAPTCHA image is generated dynamically
3. A perception-based question is asked
4. User interaction behavior is recorded
5. ML model analyzes behavior
6. System:
   - Verifies CAPTCHA
   - Classifies user as Human/Bot
7. Difficulty adjusts dynamically

---

📈 Difficulty Levels

🟢 Easy

- First 2 characters
- Last 2 characters
- Characters near top/bottom
- Larger / smaller characters

🟡 Medium

- Tilted characters
- Blurred characters
- Different fonts
- Compressed characters

🔴 Hard

- Overlapping characters
- Characters intersected by curves

---

🧪 Evaluation Metrics

- Number of attempts
- Human score (%)
- CAPTCHA accuracy
- Time taken
- Behavior pattern analysis

---

📂 Project Structure

HNP-captcha/
│── server.py
│── index.html
│── model.pkl
│── accuracy.pkl
│── requirements.txt
│── dataset/
│── my-Website/

---

▶️ How to Run

1. Install dependencies

pip install -r requirements.txt

2. Run server

python server.py

3. Open browser

http://127.0.0.1:5000

---

📊 Sample Output

- Human Score: 85%
- Classification: HUMAN ✅
- Difficulty: Medium

---

🔮 Future Improvements

- Deep Learning-based CAPTCHA generation
- Real-time bot detection enhancement
- Cloud deployment
- Mobile support

---

👩‍💻 Author

AnjanA G Kumar
B.Tech Computer Science

---

📜 License

This project is for educational purposes.
