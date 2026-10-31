from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") 
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_excel(os.path.join(BASE_DIR, "knowledge_base.xlsx"), header=1)
    df = df.dropna() # حذف أي صفوف فاضية
    print(f"تم تحميل قاعدة المعرفة: {len(df)} سؤال")
except Exception as e:
    print(f"خطأ في تحميل قاعدة المعرفة: {e}")
    df = pd.DataFrame(columns=["السؤال", "الجواب"])

def get_answer(user_question):
    knowledge_text = ""
    for index, row in df.iterrows():
        knowledge_text += f"سؤال: {row['السؤال']} | الجواب: {row['الجواب']}\n"

    prompt = f"""
    أنت مساعد ذكي خاص بكلية علوم الحاسوب وتقانة المعلومات في جامعة العلوم والتقانة.
    مهمتك: الإجابة على سؤال الطالب بدقة شديدة بالاعتماد *فقط* على قاعدة المعرفة المرفقة.
    
    القواعد:
    1. افهم معنى سؤال الطالب مهما كانت اللهجة (سودانية، فصحى، عامية).
    2. ابحث في قاعدة المعرفة عن السؤال الأقرب في *المعنى* وليس الكلمات.
    3. إذا وجدت الإجابة، اكتب الجواب فقط بدون أي مقدمات أو إضافات.
    4. إذا لم تجد الإجابة، اكتب فقط الجملة التالية: "السؤال ده مش موجود في قاعدة المعرفة".
    
    قاعدة المعرفة:
    {knowledge_text}
    
    سؤال الطالب: {user_question}
    
    الجواب:
    """

    try:
        
        response = model.generate_content(prompt)
        answer = response.text.strip()
        
        
        if "مش موجود" in answer or "لم أجد" in answer:
            return "السؤال ده مش موجود في قاعدة المعرفة"
        
        return answer
    except Exception as e:
        print(f"Error: {e}")
        return "حدث خطأ في الاتصال بالذكاء الاصطناعي."

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