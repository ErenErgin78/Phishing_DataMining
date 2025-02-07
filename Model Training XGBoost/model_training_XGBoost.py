# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 19:08:08 2025

@author: Eren
"""

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle


file_path = "final_url_features.csv"
df = pd.read_csv(file_path)

#  Kategorik değişkenleri encode et
categorical_columns = ["subdomain", "root_domain", "domain_extension"]
for col in categorical_columns:
    df[col] = LabelEncoder().fit_transform(df[col].astype(str))

#  Özellikler ve hedef değişken
X = df.drop(columns=["status"])
y = df["status"]

#  Eksik verileri doldur
X.fillna(0, inplace=True)

#  Eğitim ve test setleri
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model
model = xgb.XGBClassifier(
    n_estimators=150,
    learning_rate=0.05,
    max_depth=4,
    reg_alpha=0.1,
    reg_lambda=0.5,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=31,
    use_label_encoder=False
)

# Eğitim
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

# Tahmin
y_pred = model.predict(X_test)

# Skor
accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)

# Sonuçları kaydet
results_df = pd.DataFrame({"y_true": y_test, "y_pred": y_pred})
results_df.to_csv("xgboost_predictions.csv", index=False)

# Modeli kaydet (JSON ve Pickle formatında)
model.save_model("xgboost_model.json")

with open("xgboost_model.pkl", "wb") as file:
    pickle.dump(model, file)

# Sonuçları yazdır
print(f"Accuracy: {accuracy}")
print(classification_rep)
print("Model ve tahminler kaydedildi.")
