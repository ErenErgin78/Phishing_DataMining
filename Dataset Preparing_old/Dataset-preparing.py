# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 15:46:26 2025

@author: Eren
"""

import pandas as pd
import os

# Dosya isimleri
csv_file1 = "mixed_links.csv"     
csv_file2 = "converted_phishing.csv" 
csv_file3 = "secure_links.csv"
csv_file4 = "secure_links2.csv"
csv_file5 = "secure_links3.csv"
merged_csv = "merged_links.csv"    # Geçici birleşmiş dosya
duplicate_csv = "duplicate_links.csv"  # Tekrar eden satırlar buraya kaydedilecek
cleaned_csv = "main.csv"  # Temizlenmiş veri kaydedilecek

# 1. CSV Dosyalarını Okuma (Bozuk satırları atla ve sil)
def load_csv(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, delimiter=",", quotechar='"', on_bad_lines="skip")
        
        # Boş değerleri kontrol et ve sil
        df = df.dropna()

        # Sütun isimlerini manuel olarak kontrol et
        df.columns = ["url", "status"]

        # `status` sütununun sadece 0 ve 1 içermesini sağla
        df = df[df["status"].astype(str).isin(["0", "1"])]

        # `status` sütununu tam sayı yap
        df["status"] = df["status"].astype(int)

        return df
    else:
        print(f"Hata: {file_path} bulunamadı!")
        return pd.DataFrame(columns=["url", "status"])  # Boş DataFrame

# CSV Dosyalarını Yükle
df1 = load_csv(csv_file1)
df2 = load_csv(csv_file2)
df3 = load_csv(csv_file3)
df4 = load_csv(csv_file4)
df5 = load_csv(csv_file5)

# 2. Dosyaları Birleştirme (mixed_links, converted_phishing, secure_links sırasıyla)
merged_data = pd.concat([df1, df2, df3, df4, df5])

# 3. Tekrar eden satırları belirleme ve ayrı bir dosyaya kaydetme
duplicate_rows = merged_data[merged_data.duplicated(subset=["url"], keep=False)]
duplicate_rows.to_csv(duplicate_csv, index=False, encoding="utf-8")
print(f"Tekrar eden satırlar {duplicate_csv} olarak kaydedildi!")

# 4. Tekrar eden satırları temizleme ve temizlenmiş CSV'yi kaydetme
cleaned_data = merged_data.drop_duplicates(subset=["url"], keep=False)

# **Sadece 2 sütun içermesini garanti et**
cleaned_data = cleaned_data[["url", "status"]]

# **Dosyayı tam sayı formatında kaydet**
cleaned_data.to_csv(cleaned_csv, index=False, encoding="utf-8")
print(f"{cleaned_csv} dosyası oluşturuldu! Tekrar eden ve bozuk satırlar kaldırıldı.")

# 5. Konsola tekrar eden satır sayısını yazdırma
print(f"Tekrar eden satır sayısı: {len(duplicate_rows)}")

# 6. 1 ve 0'ların oranlarını ve sayısını hesaplama
if os.path.exists(cleaned_csv):
    df = pd.read_csv(cleaned_csv)

    # **Sadece tam sayı olan 0 ve 1 değerlerini içeren satırları al**
    df = df[df["status"].isin([0, 1])]

    # 1 ve 0'ların sayısını hesaplama
    label_counts = df["status"].value_counts()

    # Oranları hesaplama
    total = label_counts.sum()
    label_ratios = (label_counts / total) * 100

    # Sonuçları ekrana yazdırma
    print("\n### 1 ve 0'ların Dağılımı ###")
    for label in [0, 1]:  # Sadece 0 ve 1'i yazdır
        if label in label_counts:
            print(f"{label}: {label_counts[label]} adet ({label_ratios[label]:.2f}%)")
        else:
            print(f"{label}: 0 adet (0.00%)")

else:
    print(f"Hata: {cleaned_csv} bulunamadı!")
