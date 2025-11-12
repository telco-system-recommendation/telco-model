# Telco Customer EDA — Executive Summary

## 1. Overview

* **Dataset:** 10,000 customers, 12 columns (behavioral, spend, plan, device).
* **Objective:** Memahami perilaku pelanggan untuk meningkatkan rekomendasi produk dan strategi pertumbuhan berbasis data.

---

## 2. Key Insights

### Customer Profile

* **Prepaid 61%**, **Postpaid 39%** → dominasi Prepaid (perlu diatasi saat modeling).
* **Offer distribution:** General Offer (60.7%) mendominasi; peluang besar untuk personalisasi.

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
* **Chi-square:** p ≈ 0.88 → device_brand tidak berasosiasi dengan plan_type.

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
