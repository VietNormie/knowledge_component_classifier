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
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt 
import unicodedata  
import json
 
df = pd.read_csv("C:\\Users\\Admin\\knowledge_component\\input_10\\nbc_data_top_10.csv")

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
        if cat.startswith("L") or ch.isdigit() or ch.isspace():
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

# df['KC'] = df['KC'].apply(extract_code) 

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

# 4. SPLIT DATA 
X = df["Content_cleaned"].tolist() 
y = df["KC"].tolist()

X_train_val, X_test, y_train_val, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_val, y_train_val,
    test_size=0.25,
    random_state=42,
    stratify=y_train_val
)

print("Kích thước các tập sau khi chia:")
print("Train     :", len(X_train))
print("Validation:", len(X_val))
print("Test      :", len(X_test)) 

# 5. FEATURE EXTRACTION & FINE-TUNE 
ngram_options = [(1,1), (1,2), (1, 3)]
alpha_options = [0.1, 1.0, 2.0]

best_val_acc = 0.0
best_params = {"ngram_range": None, "alpha": None}

for ngram in ngram_options:
    vect = CountVectorizer(
        max_df=0.9,
        min_df=2,
        ngram_range=ngram,  
    )
    X_train_vec = vect.fit_transform(X_train)
    X_val_vec = vect.transform(X_val)

    for alpha in alpha_options:
        clf = MultinomialNB(alpha=alpha)
        clf.fit(X_train_vec, y_train) 

        y_val_pred = clf.predict(X_val_vec)
        val_acc = accuracy_score(y_val, y_val_pred)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_params["ngram_range"] = ngram
            best_params["alpha"] = alpha

print(">>> Kết quả fine-tune trên tập validation:")
print("Best validation accuracy:", best_val_acc)
print("Best ngram_range        :", best_params["ngram_range"])
print("Best alpha              :", best_params["alpha"])

# 6. FINAL 
X_train_full = X_train 
y_train_full = y_train

vect_final = CountVectorizer(
    max_df=0.9, 
    min_df=2,
    ngram_range=best_params["ngram_range"] 
)

X_train_full_vec = vect_final.fit_transform(X_train_full)
X_test_vec = vect_final.transform(X_test)

clf_final = MultinomialNB(alpha=best_params["alpha"])
clf_final.fit(X_train_full_vec, y_train_full)

y_test_pred = clf_final.predict(X_test_vec)

print("=== KẾT QUẢ TRÊN TẬP TEST ===")
print("Accuracy:", accuracy_score(y_test, y_test_pred))

print("\nClassification report:")
print(classification_report(y_test, y_test_pred))

labels_ordered = clf_final.classes_  
cm = confusion_matrix(y_test, y_test_pred, labels=labels_ordered)
print("\nConfusion matrix (rows=actual, cols=predicted):")
print(cm)

# Export vectorizer vocabulary 
vect_data = {
    "vocabulary": vect_final.vocabulary_  # token → column index
}
with open("vectorizer.json", "w", encoding="utf-8") as f:
    json.dump(vect_data, f, ensure_ascii=False)

# Export classifier parameters 
clf_data = {
    "classes": clf_final.classes_.tolist(),               # list labels
    "class_log_prior": clf_final.class_log_prior_.tolist(),
    "feature_log_prob": clf_final.feature_log_prob_.tolist()  # shape (n_classes, n_features)
}
with open("nbc_model.json", "w", encoding="utf-8") as f:
    json.dump(clf_data, f, ensure_ascii=False)











