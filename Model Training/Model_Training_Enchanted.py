import pandas as pd
import re
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score
import joblib


file_path = "main.csv"

df = pd.read_csv(file_path, low_memory=False)  # Büyük dosya için optimize edildi

# Özellik mühendisliği
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

features_list = [extract_features(url) for url in df['url']]
features_df = pd.DataFrame(features_list)

# Hedef değişken
features_df['status'] = df['status']

# Feature Engineered veriyi kaydet
features_output_path = "feature_engineered_data.csv"
features_df.to_csv(features_output_path, index=False)
print(f"Feature Engineering yapılmış veri kaydedildi: {features_output_path}")

# Özellikleri ve hedef değişkeni ayır
X = features_df.drop(columns=['status'])
y = features_df['status']

# Veriyi eğitim ve test setlerine ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=42)

# GPU DESTEKLİ LightGBM Modeli 
model = LGBMClassifier(
    n_estimators=200,      # Ağaç sayısı (Çok fazla artırmaya gerek yok, GPU zaten hızlı çalışıyor)
    max_depth=20,          # Maksimum derinlik
    learning_rate=0.05,    # Öğrenme hızı (hız & doğruluk dengesi)
    boosting_type='gbdt',  # Geleneksel Gradient Boosting
    device='gpu',          # **GPU Kullanımı Açık**
    gpu_platform_id=0,     # GPU seçimi (Varsayılan: 0)
    gpu_device_id=0,       # Eğer farklı bir GPU varsa değiştirilebilir
    random_state=42
)

# Eğitim
model.fit(X_train, y_train)

# Tahmin
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"🚀 LightGBM GPU Model Doğruluğu: {accuracy:.4f}")

# 📌 En iyi modeli kaydet
model_path = "optimized_lightgbm_gpu_model.pkl"
joblib.dump(model, model_path)
print(f"✅ En iyi GPU hızlandırılmış LightGBM modeli kaydedildi: {model_path}")

# 📌 Yeni URL için tahmin yapma fonksiyonu
def predict_url(url):
    features = extract_features(url)
    input_data = pd.DataFrame([features])
    prediction = model.predict(input_data)
    return "Phishing" if prediction[0] == 1 else "Güvenli"

# 📌 Örnek kullanım
url_test = "https://example.com/login"
print(f"🔎 URL: {url_test} - Tahmin: {predict_url(url_test)}")
