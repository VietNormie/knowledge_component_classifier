# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 09:06:24 2025

@author: Admin
"""

# 1. IMPORT LIBRARY AND LOAD DATA

import pandas as pd
from bs4 import BeautifulSoup
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression 
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt 
import unicodedata  
import json
from imblearn.over_sampling import RandomOverSampler
from collections import Counter 
from imblearn.over_sampling import SMOTE 
 
df = pd.read_csv("C:\\Users\\Admin\\knowledge_component_classifier\\input_10\\nbc_data_top_10.csv")

# 2. PREPROCESSING 

# Hàm làm sạch HTML => text thuần
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    # Xóa thẻ <img> và <math> nếu có
    for img in soup.find_all("img"):
        img.decompose() 
    for math_tag in soup.find_all("math"):
        math_tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return text

# Normalize & remove non‐alphanumeric
def normalize_text(text):
    text = text.lower()
    chars = []
    for ch in text:
        cat = unicodedata.category(ch)
        # Nếu bắt đầu bằng "L" (letter), hoặc digit, hoặc space - giữ; còn lại - thay " "
        if cat.startswith("L") or ch.isdigit() or ch.isspace() or ch == '^':
            chars.append(ch)
        else:
            chars.append(" ")
    text = "".join(chars)
    # Xóa khoảng trắng thừa
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_html(content_html: str) -> str:
    s = clean_html(content_html)
    s = normalize_text(s)
    return s

df["Content_cleaned"] = df["Content"].apply(lambda h: preprocess_html(h))

def extract_code(label: str) -> str:
    # split tại " – "  
    # Nếu chuỗi không chứa " – " thì vẫn trả về nguyên label.
    parts = label.split("-")
    code_part = parts[0].strip()
    return code_part

df['KC'] = df['KC'].apply(extract_code) 

# 3. EDA 
print("====== EDA ======")
print("Tổng số dòng dữ liệu:", len(df))
print("\nPhân phối nhãn (KC):\n", df["KC"].value_counts(), "\n")

df["num_tokens"] = df["Content_cleaned"].apply(lambda x: len(x.split()))
print("Thống kê số từ (tokens) trong mỗi văn bản:")
print(df["num_tokens"].describe())

plt.figure(figsize=(6,4))
plt.hist(df["num_tokens"], bins=10)
plt.title("Phân phối số từ trong mỗi văn bản")
plt.xlabel("Số từ")
plt.ylabel("Số văn bản")
plt.tight_layout()
plt.show()

# 4. SPLIT DATA & UPSAMPLING 

X_train, X_test, y_train, y_test = train_test_split(
    df["Content_cleaned"], df['KC'],
    test_size=0.2,
    random_state=42,
    stratify=df['KC'] 
)

print("Kích thước các tập sau khi chia:")
print("Train:", len(X_train))
print("Test :", len(X_test)) 

# 5. FEATURE EXTRACTION 

vect = CountVectorizer()
# vect = TfidfVectorizer()
X_train_vec = vect.fit_transform(X_train)
X_test_vec = vect.transform(X_test)

print(Counter(y_train))
    
# ros = RandomOverSampler(sampling_strategy='not majority')
# X_train_vec, y_train = ros.fit_resample(X_train_vec, y_train)

smote = SMOTE(sampling_strategy='not majority') 
X_train_vec, y_train = smote.fit_resample(X_train_vec, y_train)

print(Counter(y_train))

model = MultinomialNB()
# model = LogisticRegression() 

model.fit(X_train_vec, y_train) 

y_test_pred = model.predict(X_test_vec)
test_acc = accuracy_score(y_test, y_test_pred)

print("Kết quả trên tập test:")
print("Test accuracy:", test_acc)

# 6. FINAL 
print("\nClassification report:")
print(classification_report(y_test, y_test_pred))

labels_ordered = model.classes_  
cm = confusion_matrix(y_test, y_test_pred, labels=labels_ordered)
print("\nConfusion matrix (rows=actual, cols=predicted):")
print(cm)

# Export vectorizer vocabulary 
vect_data = {
    "vocabulary": vect.vocabulary_  # token -> column index
}
with open("vectorizer.json", "w", encoding="utf-8") as f:
    json.dump(vect_data, f, ensure_ascii=False)

# Export classifier parameters 
model_data = {
    "classes": model.classes_.tolist(),               # list labels
    "class_log_prior": model.class_log_prior_.tolist(),
    "feature_log_prob": model.feature_log_prob_.tolist()  # shape (n_classes, n_features)
}
with open("nbc_model.json", "w", encoding="utf-8") as f:
    json.dump(model_data, f, ensure_ascii=False)











