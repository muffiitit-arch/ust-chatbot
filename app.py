from flask import Flask, render_template, request, jsonify
import pickle
import os
import re
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# 1. تحميل العقل الجاهز (الملف اللي عملناه)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(BASE_DIR, 'vectors.pkl'), 'rb') as f:
        vectorizer, vectors, questions, answers = pickle.load(f)
    print(f"تم تحميل {len(questions)} سؤال بنجاح!")
except Exception as e:
    print(f"خطأ في التحميل: {e}")

# دالة التنظيف (لازم تكون نفس اللي في السكريبت الأول)
def clean(text):
    text = str(text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def get_answer(user_question):
    if not questions:
        return "حدث خطأ في قاعدة المعرفة."

    # تنظيف سؤال الطالب وتحويله لأرقام
    user_q_clean = clean(user_question)
    user_vector = vectorizer.transform([user_q_clean])

    # حساب التشابه الدلالي
    similarities = cosine_similarity(user_vector, vectors)[0]
    
    # جلب أعلى نسبة
    best_idx = similarities.argmax()
    best_score = similarities[best_idx]

    # العتبة 60% (لو قريبة جداً رد، لو بعيدة اعتذر)
    if best_score >= 0.60:
        return answers[best_idx]
    else:
        return "السؤال ده مش موجود في قاعدة المعرفة. يُرجى التواصل مع شؤون التسجيل."

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