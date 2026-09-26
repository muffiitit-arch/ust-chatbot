from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
from rapidfuzz import process, fuzz
import re
import requests
import secrets
import urllib.parse
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "ust_chatbot_secret_key_2026"

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

import os
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "")


try:
    df = pd.read_excel("knowledge_base.xlsx", header=1)
except Exception as e:
    print(f"خطأ في تحميل قاعدة المعرفة: {e}")
    df = pd.DataFrame(columns=["السؤال", "الجواب"])

def normalize_arabic(text):
    text = str(text)
    synonyms = {
        "ازاي": "كيف", "إزاي": "كيف", "ايه": "ما", "عايز": "اريد",
        "عاوز": "اريد", "باسورد": "كلمة المرور", "رقم القيد": "الرقم الجامعي",
        "الجامعه": "الجامعة"
    }
    for word, replacement in synonyms.items():
        text = text.replace(word, replacement)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[ًٌٍَُِّْ]', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def get_answer(user_question):
    questions = df["السؤال"].apply(normalize_arabic).tolist()
    user_q = normalize_arabic(user_question)
    if len(user_q.split()) <= 1:
        return "ممكن توضح سؤالك أكتر؟"
    match = process.extractOne(user_q, questions, scorer=fuzz.token_set_ratio)
    if match:
        matched_question, score, index = match
        if score >= 45:
            return df.iloc[index]["الجواب"]
    return "عذرًا لم أفهم سؤالك. حاول إعادة صياغته"

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login/google")
def google_login():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return redirect(auth_url)

@app.route("/login/google/authorized")
def google_authorized():
    code = request.args.get("code")
    state = request.args.get("state")
    if not code:
        return "No code provided", 400
    if state != session.get("oauth_state"):
        return "Invalid state", 400
    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    )
    token_data = token_response.json()
    if "access_token" not in token_data:
        return f"Error: {token_data}", 400
    session["logged_in"] = True
    return redirect(url_for("chat_page"))

@app.route("/chat")
def chat_page():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_question = data.get("question", "")
    answer = get_answer(user_question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)