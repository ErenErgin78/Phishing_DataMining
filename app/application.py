# -*- coding: utf-8 -*-
"""
Updated on Fri Feb 7 2025

@author: Eren (XGBoost + Streamlit)
"""

import streamlit as st
import pandas as pd
import re
import tldextract
from urllib.parse import urlparse
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

# 📌 Modeli yükle (Artık JSON formatında)
try:
    model = xgb.Booster()
    model.load_model("app/xgboost_model.json")
    st.success("XGBoost Model (JSON) başarıyla yüklendi")
except Exception as e:
    st.error(f"Model yüklenirken hata oluştu: {e}")
    st.stop()

# 📌 Modelin eğitimde kullandığı tam sütun sırası
feature_order = [
    "url_length", "num_digits", "num_at", "num_percent20", "num_special_chars",
    "num_parameters", "num_fragments", "subdomain", "root_domain", "domain_extension",
    "has_http", "has_https", "has_ip"
]

# 📌 Kullanıcıdan alınan URL'yi tam olarak veri setindeki işlemlerden geçiren fonksiyon
def process_url(url):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed_url = urlparse(url)
    extracted = tldextract.extract(parsed_url.netloc)

    # 📌 Özellikleri oluştur
    features = {
        "url_length": len(url),
        "num_digits": sum(c.isdigit() for c in url),
        "num_at": url.count("@"),
        "num_percent20": url.count("%20"),
        "num_special_chars": sum(not c.isalnum() for c in url),
        "num_parameters": url.count("?"),
        "num_fragments": url.count("#"),
        "subdomain": extracted.subdomain if extracted.subdomain else "none",
        "root_domain": f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain,
        "domain_extension": extracted.suffix if extracted.suffix else "unknown",
        "has_http": 1 if "http://" in url else 0,
        "has_https": 1 if "https://" in url else 0,
        "has_ip": 1 if re.match(r"(\d{1,3}\.){3}\d{1,3}", parsed_url.netloc) else 0
    }

    return pd.DataFrame([features])

# 📌 Kategorik değişkenleri encode eden fonksiyon
def encode_categorical_features(df):
    categorical_columns = ["subdomain", "root_domain", "domain_extension"]
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))  
    return df

# 📌 Streamlit Arayüzü
st.title("🔍 XGBoost Phishing URL Detector")
st.write("Lütfen analiz etmek istediğiniz URL'yi girin ve 'Detect' butonuna basın.")

# 📌 Kullanıcıdan input
url_input = st.text_input("URL Girin:", "")

if st.button("Detect"):
    if url_input:
        # 📌 URL'yi işle
        input_data = process_url(url_input)

        # 📌 Kategorik değişkenleri encode et
        input_data = encode_categorical_features(input_data)

        # 📌 Modelin eğitim sırası ile uyumlu hale getir
        input_data = input_data[feature_order]

        # 📌 Model ile tahmin yap (DMatrix kullanarak)
        dmatrix_data = xgb.DMatrix(input_data)
        prediction = model.predict(dmatrix_data)[0]
        predicted_class = 1 if prediction > 0.5 else 0  # 0.5 eşik değeri

        # 📌 Sonuç
        if predicted_class == 1:
            st.success("✅ SAFE - Bu site güvenli görünüyor.")
            st.markdown(
                "<div style='background-color:#27AE60; padding:15px; border-radius:10px; text-align:center; color:white;'>"
                "<h2>✅ SAFE</h2></div>",
                unsafe_allow_html=True
            )
        else:
            st.error("⚠️ PHISHING DANGER - Bu site şüpheli olabilir!")
            st.markdown(
                "<div style='background-color:#E74C3C; padding:15px; border-radius:10px; text-align:center; color:white;'>"
                "<h2>⚠️ PHISHING DANGER</h2></div>",
                unsafe_allow_html=True
            )
    else:
        st.warning("Lütfen bir URL girin!")
