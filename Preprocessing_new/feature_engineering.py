# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 18:05:50 2025

@author: Eren
"""

import pandas as pd
import re
import tldextract
from urllib.parse import urlparse

# CSV yükle
file_path = "new_main.csv"
df = pd.read_csv(file_path)

# Yeni DataFrame
features_df = pd.DataFrame()

# URL string özellikleri
features_df["url_length"] = df["url"].apply(len)
features_df["num_digits"] = df["url"].apply(lambda x: sum(c.isdigit() for c in x))
features_df["num_at"] = df["url"].apply(lambda x: x.count("@"))
features_df["num_percent20"] = df["url"].apply(lambda x: x.count("%20"))
features_df["num_special_chars"] = df["url"].apply(lambda x: sum(not c.isalnum() for c in x))
features_df["num_parameters"] = df["url"].apply(lambda x: x.count("?"))
features_df["num_fragments"] = df["url"].apply(lambda x: x.count("#"))

# Domain ayrıştırma
def extract_domain_info(url):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    if "[" in url and "]" in url:
        return "ipv6", "ipv6", "ipv6"
    
    try:
        parsed_url = urlparse(url)
        extracted = tldextract.extract(parsed_url.netloc)
        subdomain = extracted.subdomain
        root_domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain
        domain_extension = extracted.suffix if extracted.suffix else "unknown"
        return subdomain, root_domain, domain_extension
    except:
        return "error", "error", "error"

features_df[["subdomain", "root_domain", "domain_extension"]] = df["url"].apply(lambda x: pd.Series(extract_domain_info(x)))

# HTTP/HTTPS kontrolü
features_df["has_http"] = df["url"].apply(lambda x: 1 if "http://" in x else 0)
features_df["has_https"] = df["url"].apply(lambda x: 1 if "https://" in x else 0)

# IP tespiti
ipv4_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
ipv6_pattern = re.compile(r'\[?[a-fA-F0-9:]+\]?')
features_df["has_ip"] = df["url"].apply(lambda x: 1 if ipv4_pattern.search(x) or ipv6_pattern.search(x) else 0)

# Status ekle
features_df["status"] = df["status"]

# Kaydet
output_path = "final_url_features.csv"
features_df.to_csv(output_path, index=False)

print(f"Tamamlandı: {output_path}")
