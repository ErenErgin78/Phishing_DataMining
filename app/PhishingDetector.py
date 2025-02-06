# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:58:23 2025

@author: Eren
"""

import streamlit as st
import joblib
import pandas as pd
import re
from urllib.parse import urlparse

try:
    model = joblib.load("app/model.pkl")
    st.success("Model başarıyla yüklendi")
except Exception as e:
    st.error(f"Model yüklenirken hata oluştu: {e}")
    st.stop()

# URL'den anlamlı veri çıkar
def extract_features(url):
    parsed_url = urlparse(url)
    features = {
        "url_length": len(url),
        "num_dashes": url.count('-'),
        "num_dots": url.count('.'),
        "https": 1 if parsed_url.scheme == "https" else 0,
        "num_digits": sum(c.isdigit() for c in url),
        "has_ip": 1 if re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", parsed_url.netloc) else 0,
        "tld_length": len(parsed_url.netloc.split('.')[-1]) if '.' in parsed_url.netloc else 0
    }
    return features

# Arayüz Başlangıcı
st.title("🔍 Phishing URL Detector")
st.write("Lütfen analiz etmek istediğiniz URL'yi girin ve 'Detect' butonuna basın.")

# Kullanıcıdan input
url_input = st.text_input("URL Girin:", "")

if st.button("Detect"):
    if url_input:
        features = extract_features(url_input)
        input_data = pd.DataFrame([features])
        
        # Model ile tahmin
        prediction = model.predict(input_data)[0]
        
        # Sonuç
        if prediction == 0:
            st.success(" SAFE - Bu site güvenli görünüyor.")
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
