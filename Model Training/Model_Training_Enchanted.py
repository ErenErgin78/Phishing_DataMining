import pandas as pd
import re
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split, cross_val_score
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score
import joblib


file_path = "main.csv"

df = pd.read_csv(file_path, low_memory=False)  # Büyük dosya için optimize edildi

# URL'yi anlamlı parçalara böl
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

features_output_path = "feature_engineered_data.csv"
features_df.to_csv(features_output_path, index=False)
print(f"Feature Engineering yapılmış veri kaydedildi: {features_output_path}")

# Özellikleri ve hedef değişkeni ayır
X = features_df.drop(columns=['status'])
y = features_df['status']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=42)

#OVERFITTING ÖNLEYİCİ LightGBM Modeli
model = LGBMClassifier(
    n_estimators=200,      
    max_depth=15,          
    learning_rate=0.05,    
    boosting_type='gbdt',  
    device='gpu',         
    gpu_platform_id=0,    
    gpu_device_id=0,     
    min_data_in_leaf=50,   
    random_state=42
)

#5-FOLD CROSS VALIDATION
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')

#Ortalama doğruluk değeri
print(f"Cross Validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

#Eğitim
model.fit(X_train, y_train)

#Tahmin
y_pred = model.predict(X_test)

#Accuracy
test_accuracy = accuracy_score(y_test, y_pred)
print(f" LightGBM GPU Model Doğruluğu (Test Seti): {test_accuracy:.4f}")

#Modeli kaydet
model_path = "optimized_lightgbm_gpu_model.pkl"
joblib.dump(model, model_path)
print(f" En iyi GPU hızlandırılmış LightGBM modeli kaydedildi: {model_path}")

# Yeni URL için tahmin yapma fonksiyonu
def predict_url(url):
    features = extract_features(url)
    input_data = pd.DataFrame([features])
    prediction = model.predict(input_data)
    return "Phishing" if prediction[0] == 1 else "Güvenli"