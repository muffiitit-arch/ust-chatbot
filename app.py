from flask import Flask, render_template, request, jsonify
import pandas as pd
from rapidfuzz import process, fuzz
import re
import os

app = Flask(__name__)

def normalize_arabic(text):
    text = str(text)
    synonyms = {
        "ازاي": "كيف", "إزاي": "كيف", "ايه": "ما",
        "عايز": "اريد", "عاوز": "اريد",
        "باسورد": "كلمة المرور", "رقم القيد": "الرقم الجامعي",
        "الجامعه": "الجامعة", "رسومات": "رسوم",
        "كيفن": "كيف", "كيفو": "كيف", "كيفك": "كيف",
        "وين": "أين", "فين": "أين",
        "شنو": "ما", "إيش": "ما", "ايش": "ما",
        "داير": "اريد",
        "بحصل": "يحصل", "بيحصل": "يحصل", "بتحصل": "تحصل",
        "بقدر": "استطيع", "بنقدر": "نستطيع", "بتقدر": "تستطيع",
        "بدخل": "ادخل", "بتدخل": "تدخل", "بيدخل": "يدخل",
        "بتعمل": "تعمل", "بيتعمل": "يعمل", "بتسوي": "تعمل",
        "أونلاين": "الكتروني", "اونلاين": "الكتروني",
        "محتاج": "احتاج", "بحتاج": "احتاج", "بتحتاج": "تحتاج",
        "وقت": "متى", "أمتى": "متى", "امتى": "متى",
        "منو": "من", "منهو": "من",
        "دي": "هذه", "ده": "هذا", "دا": "هذا", "ديل": "هؤلاء",
        "ليه": "لماذا", "ليش": "لماذا",
        "مافي": "لا يوجد", "ما في": "لا يوجد",
        "ماموجود": "لا يوجد",
    }

    for word, replacement in synonyms.items():
        text = re.sub(r'\b' + re.escape(word) + r'\b', replacement, text)

    text = re.sub(r'[إأآأ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[ًٌٍَُِّْ]', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_excel(os.path.join(BASE_DIR, "knowledge_base.xlsx"), header=1)
    df["_normalized"] = df["السؤال"].apply(normalize_arabic)
    print(f"تم تحميل قاعدة المعرفة: {len(df)} سؤال")
except Exception as e:
    print(f"خطأ في تحميل قاعدة المعرفة: {e}")
    df = pd.DataFrame(columns=["السؤال", "الجواب", "_normalized"])

GREETINGS = {
    "مرحبا", "هلا", "السلام عليكم", "صباح الخير", "مساء الخير",
    "اهلا", "أهلا", "هاي", "كيف الحال"
}

THANKS = {"شكرا", "شكراً", "تسلم", "يعطيك العافية", "شكرا جزيلا"}

def get_answer(user_question):
    cleaned = str(user_question).strip()

    if cleaned in GREETINGS:
        return "وعليكم السلام ورحمة الله! اكتب استفسارك وسأحاول مساعدتك"

    if cleaned in THANKS:
        return "العفو! تحت أمرك لو عندك سؤال تاني"

    user_q = normalize_arabic(user_question)

    if len(user_q.split()) <= 1:
        return "ممكن توضح سؤالك أكتر؟"

    match = process.extractOne(user_q, df["_normalized"].tolist(), scorer=fuzz.token_set_ratio)

    if match:
        matched_question, score, index = match
        if score >= 55:
            return df.iloc[index]["الجواب"]

    return "عذرًا، لم أتمكن من العثور على إجابة دقيقة لسؤالك"
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/chat")
def chat_page():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    user_question = data.get("question", "")
    if not user_question.strip():
        return jsonify({"answer": "اكتب سؤالك من فضلك"})
    answer = get_answer(user_question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)