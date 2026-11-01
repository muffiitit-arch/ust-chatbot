import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import re

# دالة التنظيف
def clean(text):
    text = str(text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

print("جاري تحميل الإكسل...")
df = pd.read_excel("knowledge_base.xlsx", header=1).dropna()
questions = df["السؤال"].tolist()

print("جاري فهم معاني الأسئلة...")
# هذا الجزء هو الذي يفهم الكلمات المشتركة (Semantic)
vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2))
vectors = vectorizer.fit_transform([clean(q) for q in questions])

# حفظ "العقل" بتاع البوت
with open('vectors.pkl', 'wb') as f:
    pickle.dump((vectorizer, vectors, questions, df["الجواب"].tolist()), f)

print("تم حفظ الذكاء بنجاح في vectors.pkl!")