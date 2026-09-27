from flask import Flask, render_template, request, jsonify
import pandas as pd
from rapidfuzz import process, fuzz
import re
import os

app = Flask(__name__)

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_excel(os.path.join(BASE_DIR, "knowledge_base.xlsx"), header=1)
    print(f"  خطاء في الاتصال بي المساعد  : {len(df)} سؤال")
except Exception as e:
    print(f"  خطاء في الاتصال بي المساعد   : {e}")
    df = pd.DataFrame(columns=["السؤال", "الجواب"])

def normalize_arabic(text):
    text = str(text)
    synonyms = {
        "ازاي": "كيف", "إزاي": "كيف", "ايه": "ما", "عايز": "اريد",
        "عاوز": "اريد", "باسورد": "كلمة المرور", "رقم القيد": "الرقم الجامعي",
        "الجامعه": "الجامعة", "رسومات": "رسوم",
        "كيفن": "كيف", "كيفو": "كيف", "كيفك": "كيف",
        "وين": "اين", "فين": "اين",
        "شنو": "ما", "إيش": "ما", "ايش": "ما",
        "داير": "اريد", "دائرة": "اريد",
        "بحصل": "يحصل", "بيحصل": "يحصل", "بتحصل": "تحصل",
        "بقدر": "استطيع", "بنقدر": "نستطيع", "بتقدر": "تستطيع",
        "بدخل": "ادخل", "بتدخل": "تدخل", "بيدخل": "يدخل",
        "بتعمل": "تعمل", "بيتعمل": "يعمل", "بتسوي": "تعمل",
        "اونلاين": "الكتروني",
        "محتاج": "احتاج", "بحتاج": "احتاج", "بتحتاج": "تحتاج",
        "امتى": "متى",
        "منو": "من", "منهو": "من",
        "دي": "هذه", "ده": "هذا", "دا": "هذا", "ديل": "هؤلاء",
        "ليه": "لماذا", "ليش": "لماذا",
        "مافي": "لا يوجد", "ما في": "لا يوجد",
        "ماموجود": "لا يوجد", "موجود": "هل هناك"
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
        return "يرجى كتابة سؤال أكثر تفصيلاً للحصول على إجابة دقيقة"
    match = process.extractOne(user_q, questions, scorer=fuzz.token_set_ratio)
    if match:
        matched_question, score, index = match
        if score >= 55:
            return df.iloc[index]["الجواب"]
    return "لم أتمكن من العثور على إجابة دقيقة لسؤالك. يرجى إعادة صياغة السؤال "

@app.route("/")
def login_page():
    return render_template("login.html")

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