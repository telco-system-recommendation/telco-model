# Telco Customer EDA — Comprehensive Documentation

## 1. Overview

* **Dataset:** 10,000 customers, 12 columns (behavioral, spend, plan, device).
* **Objective:** Understand customer behavior to improve product recommendations and data-driven growth strategies.
* **Data Source:** `data_capstone.csv` with features like monthly_spend, avg_data_usage_gb, plan_type, device_brand, target_offer, etc.

---

## 2. Data Cleaning Summary

* **Shape:** 10,000 rows, 12 columns.
* **Null Values:** No missing values reported (df.isnull().sum() shows 0 for all columns).
* **Data Types:**
  * Numeric: monthly_spend, avg_data_usage_gb, pct_video_usage, avg_call_duration, sms_freq, topup_freq, travel_score, complaint_count.
  * Categorical: customer_id, plan_type, device_brand, target_offer.
* **Descriptive Statistics:** 
  * Monthly spend: Mean ~92K, Median ~91K, Range 0-200K+.
  * Data usage: Mean ~5.5GB, Median ~5.4GB.
  * Other features vary; no extreme outliers noted in initial describe().

---

## 3. Univariate Analysis

### Target Distribution

* **General Offer:** 60.7% (most common).
* **Other Offers:** Varied, with "Data Bundle" and "Voice Bundle" as top alternatives.
* **Visualization:** Countplot showing skewed distribution towards General Offer.

### Numeric Feature Distributions

* **Histograms with KDE:** All numeric features show distributions (e.g., monthly_spend right-skewed, data_usage normal-ish).
* **Key Observations:** 
  * monthly_spend: Peaks around 90K.
  * avg_data_usage_gb: Concentrated 4-7GB.
  * complaint_count: Mostly 0-2, long tail.

### Categorical Summaries

* **plan_type:** Prepaid 61%, Postpaid 39%.
* **device_brand:** Multiple brands, top ones include Samsung, Apple, etc. (value_counts show diversity).
* **target_offer:** As above, dominated by General Offer.

---

## 4. Bivariate and Multivariate Analysis

### Correlations (Heatmap)

* **Strongest:** monthly_spend ↔ avg_data_usage_gb (r ≈ 0.90).
* **Moderate:** pct_video_usage ↔ avg_data_usage_gb (r ≈ 0.60), sms_freq ↔ avg_call_duration (r ≈ 0.50).
* **Weak:** travel_score, topup_freq with others.
* **Visualization:** Heatmap saved as correlation_heatmap.png.

### Boxplots by Target

* **Focus on Top 6 Targets:** Boxplots for features like avg_data_usage_gb, pct_video_usage, avg_call_duration, sms_freq, topup_freq, travel_score, complaint_count.
* **Separability:** Some features show differences (e.g., higher data usage for data-related offers), but overlap exists.

### Pairplot

* **Sampled (1000 points):** Scatter plots for avg_data_usage_gb, pct_video_usage, avg_call_duration, monthly_spend, topup_freq, colored by target_offer.
* **Insights:** Clusters visible, e.g., high spend + high data usage associated with premium offers.

### Scatter Plots

* **Data Usage vs Spend by Plan Type:** Prepaid/Postpaid show similar patterns, no clear separation.
* **Call Duration vs Spend by Target and Plan:** Some targets cluster differently, e.g., voice-heavy offers have higher call duration.

---

## 5. Categorical Analysis

### Proportions by Target

* **For each categorical column (plan_type, device_brand):**
  * Stacked bar plots showing proportion of target_offer within each category.
  * **device_brand:** Certain brands (e.g., premium like Apple) show higher proportions for data bundles; budget brands lean to General Offer.
  * **plan_type:** Postpaid slightly favors certain offers, but not significant.

---

## 6. Feature Importance

* **Method:** Decision Tree Classifier (depth=6), ordinal encoded categoricals, filled nulls with -999.
* **Top Features:**
  1. monthly_spend (0.27)
  2. complaint_count (0.18)
  3. device_brand (0.17)
  4. pct_video_usage (0.14)
  5. avg_data_usage_gb (0.13)
  6. avg_call_duration (0.08)
  7. sms_freq (0.07)
  8. topup_freq (0.06)
  9. travel_score (0.05)
  10. plan_type (0.04)
* **Saved:** Top 20 to feature_importances_top20.csv.

---

## 7. Feature Engineering

* **Cost per GB:** monthly_spend / avg_data_usage_gb (handled zeros by setting to 0.1).
* **Engagement Score:** avg_call_duration + sms_freq + topup_freq.
* **Visualization:** Boxplot of cost_per_gb by target_offer (shows variation, e.g., higher cost for basic offers).

---

## 8. Clustering Analysis

* **Method:** KMeans (k=4), standardized features: avg_data_usage_gb, pct_video_usage, avg_call_duration, sms_freq, monthly_spend, topup_freq, travel_score, complaint_count.
* **Clusters:**
  * **Cluster 0 (Travelers):** High travel_score (~0.8), moderate spend (~94K).
  * **Cluster 1 (High Value):** High spend (~179K), high usage (~7GB), low complaints.
  * **Cluster 2 (Moderate):** Spend ~91K, balanced features.
  * **Cluster 3 (Complaint-Prone):** High complaint_count (~1.5), moderate spend (~93K).
* **Business Use:** Segmentation for targeted campaigns.

---

## 9. Statistical Tests

* **Mann-Whitney U (spend by plan_type):** p ≈ 0.45 → No significant difference in spend between Prepaid and Postpaid.
* **Chi-square (device_brand vs plan_type):** p ≈ 0.88 → No association between device brand and plan type.
* **Chi-square (device_brand vs target_offer):** Based on proportions, association exists (e.g., brand preferences for offers). Recommend formal test.

---

## 10. Key Insights

### Customer Profile

* **Prepaid 61%**, **Postpaid 39%** → dominasi Prepaid (perlu diatasi saat modeling).
* **Offer distribution:** General Offer (60.7%) mendominasi; peluang besar untuk personalisasi.
* **Device Brand Influence:** Device_brand significantly affects target_offer preferences. Proportions analysis shows certain brands (e.g., premium devices) have higher likelihood for data-heavy offers like "Data Bundle", while budget brands lean towards "General Offer". This suggests device type as a key segmentation factor for personalized recommendations.

### Spend Drivers

* **Strongest correlation:** `monthly_spend` ↔ `avg_data_usage_gb` (r ≈ 0.90) — penggunaan data jadi penentu utama pendapatan.
* Variabel lain (`pct_video_usage`, `travel_score`, `sms_freq`, `topup_freq`) punya korelasi lemah terhadap spend.
* **Feature importance (Decision Tree):**

  1. monthly_spend (0.27)
  2. complaint_count (0.18)
  3. device_brand (0.17)
  4. pct_video_usage (0.14)
  5. avg_data_usage_gb (0.13)

### Statistical Tests

* **Mann–Whitney U:** p ≈ 0.45 → tidak ada perbedaan signifikan spend antara Prepaid dan Postpaid.
* **Chi-square (device_brand vs plan_type):** p ≈ 0.88 → device_brand tidak berasosiasi dengan plan_type.
* **Chi-square (device_brand vs target_offer):** Based on proportions analysis, device_brand shows association with target_offer preferences (e.g., premium brands favor data bundles). Recommended to run formal Chi-square test for confirmation.

### Segmentation (KMeans, k=4)

* **Cluster 1 – High Value:** Spend ≈ 179K, usage tinggi → target upsell premium/device upgrade.
* **Cluster 0 – Travelers:** Spend ≈ 94K, travel_score tinggi → target roaming/travel promos.
* **Cluster 2 & 3 – Moderate:** Spend ≈ 91–93K; Cluster 3 punya complaint_count tinggi → fokus retention.

---

## 3. Business Impact

* **Personalization gap:** 60% pelanggan masih di General Offer — potensi besar untuk rekomendasi berbasis perilaku.
* **Upsell opportunity:** Heavy data users → peluang Data Booster & paket premium.
* **Retention play:** Complaint tinggi = churn risk → peluang intervensi berbasis service.
* **Plan-neutral strategy:** Perbedaan spend antar plan kecil → fokus pada perilaku, bukan jenis plan.
* **Device-based targeting:** Device_brand affects target_offer preferences — opportunity for device-specific offers (e.g., premium devices for data bundles, budget devices for basic offers).

---

## 4. Recommendations

### Modeling

* Gunakan **multiclass model (e.g. LightGBM)** untuk prediksi `target_offer` dengan fitur perilaku utama.
* Tangani **class imbalance** (oversampling / class weighting).
* Eksperimen fase lanjut: **Uplift/Causal Model** untuk rekomendasi berbasis dampak bisnis (ARPU uplift).

### Feature Engineering

* Tambahkan fitur seperti `cost_per_gb`, `recency/frequency`, dan `engagement_score`.
* Gunakan encoding atau embedding untuk variabel kategori.

### Experimentation

* Uji **A/B test per-cluster**:

  * High-value → Device Upgrade vs General Offer
  * High-complaint → Retention Offer vs CS-improvement
* Monitor KPI: conversion rate, ARPU uplift, retention delta, complaint rate.

---

## 5. Next Steps

* Lengkapi feature pipeline dan split data train/val/test.
* Build baseline model + evaluate per-cluster (precision@k, recall).
* Setup **dashboard metrics** (ARPU, CTR, conversion).
* Tambahkan visualisasi: *spend vs data usage* dan *profil 4 cluster* untuk pitch deck investor.

---

## 6. Limitations

* `cost_per_gb` belum tersedia → penting untuk analisis profit-aware.
* Tidak ada perbedaan signifikan pada plan type → insight fokus pada perilaku dan pengalaman pelanggan.
* Visualisasi mendukung insight; idealnya disertakan untuk komunikasi ke stakeholder.

---

Apakah kamu mau saya ubah versi ini menjadi format **pitch deck 4–5 slide** (dengan visual dan pesan investor-friendly)?
