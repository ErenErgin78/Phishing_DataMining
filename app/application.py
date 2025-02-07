# -*- coding: utf-8 -*-
"""
Updated on Thu Feb  7 2025

@author: Eren (XGBoost Versiyonu)
"""

import streamlit as st
import joblib
import pandas as pd
import re
from urllib.parse import urlparse
import pickle
import tldextract

# 📌 Modeli yükle
try:
    with open("xgboost_model.pkl", "rb") as file:
        model = pickle.load(file)
    st.success("XGBoost Model başarıyla yüklendi")
except Exception as e:
    st.error(f"Model yüklenirken hata oluştu: {e}")
    st.stop()

# 📌 URL'den öznitelik çıkarımı (Final CSV formatına uygun hale getirildi)
def extract_features(url):
    parsed_url = urlparse(url)
    extracted = tldextract.extract(url)

    features = {
        "url_length": len(url),  # URL uzunluğu
        "num_digits": sum(c.isdigit() for c in url),  # Rakam sayısı
        "num_special_chars": sum(not c.isalnum() for c in url),  # Özel karakter sayısı
        "num_parameters": url.count("?"),  # Sorgu parametre sayısı
        "num_fragments": url.count("#"),  # Fragment sayısı (# işareti)
        "has_https": 1 if parsed_url.scheme == "https" else 0,  # HTTPS olup olmadığı
        "has_http": 1 if "http://" in url else 0,  # HTTP olup olmadığı
        "has_ip": 1 if re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", parsed_url.netloc) else 0,  # IP içeriyor mu?
        "subdomain": extracted.subdomain,  # Subdomain (alt alan adı)
        "root_domain": f"{extracted.domain}.{extracted.suffix}",  # Root domain
        "domain_extension": extracted.suffix  # Alan adı uzantısı (.com, .net)
    }
    
    return features

# 📌 Arayüz Başlangıcı
st.title("🔍 XGBoost Phishing URL Detector")
st.write("Lütfen analiz etmek istediğiniz URL'yi girin ve 'Detect' butonuna basın.")

# 📌 Kullanıcıdan input
url_input = st.text_input("URL Girin:", "")

if st.button("Detect"):
    if url_input:
        features = extract_features(url_input)
        input_data = pd.DataFrame([features])

        # 📌 Kategorik değişkenleri encode et (Subdomain, Root Domain, Domain Uzantısı)
        try:
            label_encoders = joblib.load("label_encoders.pkl")
            for col in ["subdomain", "root_domain", "domain_extension"]:
                if input_data[col][0] not in label_encoders[col].classes_:
                    input_data[col] = "unknown"  # Yeni değerler için
                input_data[col] = label_encoders[col].transform([input_data[col][0]])
        except Exception as e:
            st.error(f"Kategorik değişkenler encode edilirken hata: {e}")
            st.stop()

        # 📌 Model ile tahmin
        prediction = model.predict(input_data)[0]

        # 📌 Sonuç
        if prediction == 0:
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
