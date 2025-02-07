# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 22:46:09 2025

@author: Eren
"""

import xgboost as xgb
import pandas as pd

# 📌 Modeli JSON formatında yükle
model_path = "xgboost_model.json"  # JSON model dosyanın adı
model = xgb.Booster()
model.load_model(model_path)

# 📌 Modelin özellik önem sırasını al (SAFE = status 0'ı güçlendirenler)
feature_importance = model.get_score(importance_type="weight")

# 📌 Özellikleri önem sırasına göre sıralayalım
importance_df = pd.DataFrame(list(feature_importance.items()), columns=["Feature", "Importance"])
importance_df = importance_df.sort_values(by="Importance", ascending=False)

# 📌 En çok SAFE (status=0) olasılığını artıran ilk 10 özelliği göster
print("✅ SAFE (status=0) olasılığını en çok artıran özellikler:")
print(importance_df.head(20))
