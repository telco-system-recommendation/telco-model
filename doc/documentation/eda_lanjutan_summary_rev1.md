# 📘 **Telco Customer EDA — Comprehensive Documentation (Berbasis Output EDA 1–30)**

## 1. Overview

Dataset Telco berisi **10.000 pelanggan dengan 12 fitur**, mencakup perilaku penggunaan (data, video, call, SMS), spending bulanan, frekuensi top-up, brand device, serta target offer dari perusahaan.

**Tujuan EDA:**
Memahami pola penggunaan layanan, segmentasi pelanggan, faktor yang mempengaruhi rekomendasi produk, serta mempersiapkan fitur untuk modeling prediksi *target_offer*.

Fitur utama mencakup:

* **Behavioral:** avg_data_usage_gb, pct_video_usage, avg_call_duration, sms_freq, topup_freq
* **Financial:** monthly_spend
* **Risk/Experience:** complaint_count
* **Profile:** plan_type, device_brand
* **Target:** target_offer

---

# 2. Data Cleaning Summary

### Struktur Dataset

* **Rows:** 10,000
* **Columns:** 12

### Missing & Duplicate Check

* **Tidak ada missing value**
* **Tidak ada duplikasi**

### Logical Value Check

* Diagram: *Range Check Table*
* Hasil:

  * Semua fitur memiliki rentang nilai yang logis.
  * Ada **2 nilai monthly_spend negatif**, perlu diperbaiki atau dihapus.

### Descriptive Summary

* **Monthly spend:** sangat variatif, mulai 0 hingga >450.000 → indikasi outlier.
* **Avg data usage:** mayoritas 3–6 GB.
* *Tidak ada fitur yang tampak salah format.*

---

# 3. Univariate Analysis (Distribusi Per Fitur)

Untuk tiap fitur numerik, kamu menampilkan:
📌 **Histogram + KDE** → untuk melihat distribusi
📌 **Q–Q Plot** → untuk normalitas
📌 **Outlier Impact Plot** → pengaruh outlier pada mean

Berikut ringkasannya.

---

## 3.1 avg_data_usage_gb

**Diagram:** Histogram + KDE, Q–Q Plot

**Distribusi:**

* **Right-skewed** (ekor panjang ke kanan)
* Mayoritas pelanggan menggunakan **0–10 GB**, puncak sekitar **4–6 GB**.

**Analisis:**

* Tidak berdistribusi normal (ditunjukkan oleh Q–Q plot menyimpang dari garis).
* Banyak outlier di penggunaan data tinggi (hingga ~40 GB).
* Cocok menggunakan transformasi log jika dibutuhkan modeling.

---

## 3.2 pct_video_usage

**Diagram:** Histogram + KDE, Q–Q Plot

**Distribusi:**

* Hampir **simetris**, berbentuk unimodal dengan puncak di 0.3–0.5.
* Q–Q plot menunjukkan sedikit deviasi di ekor → tidak normal sempurna.

**Analisis:**

* Pelanggan rata-rata 30–50% penggunaan datanya berasal dari video.
* Perlu dicek hubungannya dengan data usage dan spending.

---

## 3.3 avg_call_duration

**Diagram:** Histogram + KDE, Q–Q Plot

**Distribusi:**

* Mendekati **normal distribution**
* Q–Q plot hampir linear.

**Analisis:**

* Perilaku durasi telepon pelanggan stabil dan tidak banyak outlier.
* Fitur ideal untuk model linear.

---

## 3.4 sms_freq

**Diagram:** Histogram + KDE, Q–Q Plot

**Distribusi:**

* **Right-skewed**, nilai kecil yang dominan.
* Banyak pelanggan jarang mengirim SMS.

**Analisis:**

* Distribusi diskret → tidak cocok ditransformasi log.
* Perlu scaling khusus untuk algoritma tertentu.

---

## 3.5 topup_freq

**Diagram:** Histogram + KDE, Q–Q Plot

**Distribusi:**

* Berbentuk diskret, **multi-modal** (frekuensi tertentu dominan).
* Q–Q plot menunjukkan penyimpangan besar, tidak normal.

**Analisis:**

* Perilaku top-up mengikuti pola kebiasaan paket mingguan atau bulanan.
* Outlier tidak ekstrem.

---

## 3.6 monthly_spend

**Diagram:** Histogram + KDE, Q–Q Plot

**Distribusi:**

* **Sangat right-skewed**, dengan banyak outlier besar.
* Q–Q plot menunjukkan deviasi besar → *highly non-normal*.
* Outlier mempengaruhi mean (ditunjukkan Outlier Impact Plot).

**Analisis:**

* Spending pelanggan bervariasi sangat besar.
* Perlu normalisasi atau winsorization.
* Fitur terpenting untuk prediksi offer.

---

# 4. Bivariate Analysis

## 4.1 avg_data_usage_gb vs monthly_spend

**Diagram:** Scatterplot + Regression Line

**Insight:**

* Hubungan **linear positif yang kuat** → semakin besar penggunaan data, semakin besar pengeluaran.
* Outlier spending tinggi muncul pada high data usage.

---

## 4.2 pct_video_usage vs avg_data_usage_gb

**Diagram:** Scatterplot

**Insight:**

* Tidak linear.
* Pelanggan dengan penggunaan video tinggi sering memiliki penggunaan data tinggi, tetapi tidak selalu sebaliknya.

---

# 5. Outlier Analysis

## 5.1 Outlier Count

Fitur dengan outlier terbanyak:

1. monthly_spend
2. avg_data_usage_gb
3. complaint_count

## 5.2 Outlier Impact Plot

Diagram: Horizontal bar chart

**Insight:**

* monthly_spend memiliki **dampak terbesar terhadap mean**, artinya distribusinya sangat dipengaruhi outlier.
* Perlu treatment seperti log transform atau capping.

---

# 6. Categorical Analysis

## 6.1 Category Cardinality

Diagram: Bar chart

**Insight:**

* customer_id → 10.000 unique values (ID unik)
* device_brand → 7 brand
* plan_type → 2 kategori
* target_offer → 9 kategori (sangat imbalanced)

---

## 6.2 WordCloud (device_brand & target_offer)

**Insight:**

* Brand paling dominan: Realme, Xiaomi, Samsung.
* Target offer paling dominan: **General Offer** (overwhelmingly largest).

---

# 7. Multicollinearity & Correlation

## 7.1 Dendrogram (Hierarchical Clustering)

**Insight:**

* monthly_spend dan avg_data_usage_gb berada dalam cluster yang sama → redundansi kuat.
* pct_video_usage berdekatan dengan avg_data_usage_gb.

## 7.2 VIF

Fitur dengan multicollinearity tinggi:

* monthly_spend (VIF > 20)
* avg_data_usage_gb (VIF > 10)

---

# 8. Dimensionality Reduction

## 8.1 PCA (Plan Type)

**Insight:**

* Prepaid dan Postpaid **tidak membentuk cluster terpisah**.
* Artinya plan_type tidak menciptakan pola perilaku yang unik.

## 8.2 UMAP (Target Offer)

**Insight:**

* Terlihat *cluster nonlinear*, tetapi target_offer tetap tersebar.
* Tidak ada cluster alami yang solid berdasarkan offer.

---

# 9. Segmentation

## 9.1 Spending Segment (Q1–Q4)

Diagram: Bar chart

* Distribusi relatif merata tiap kuartil.

## 9.2 Lift Analysis

Diagram: Heatmap

**Insight:**

* High spender (Q4) cenderung menerima:

  * **Device Upgrade Offer**
  * **Data Booster**
* Low spender (Q1–Q2) → General Offer (dominan 70–80%)

---

# 10. Cohort Analysis (Device Brand x Spending Quartile)

**Diagram:** Heatmap

**Insight:**

* Realme dan Xiaomi mendominasi spender rendah.
* Apple dan Huawei lebih banyak di Q3–Q4.
* Kekuatan brand mempengaruhi potensi rekomendasi produk.

---

# 11. Radar Chart (Customer Behavior Profile)

**Insight:**

* monthly_spend jauh lebih tinggi dibanding fitur lain (skala berbeda).
* Menggambarkan pola pelanggan rata-rata: spending tinggi, usage moderat, topup kecil.

---

# 12. Key Insights Summary

### 1. **Spending & Data Usage adalah fitur paling penting**

* Korelasi kuat
* Mutual Information tertinggi
* Feature importance tertinggi

### 2. **Target Offer sangat imbalanced**

* General Offer > 60%
  → perlu weighted modeling

### 3. **Outlier sangat signifikan**

* monthly_spend → heavy tail
* butuh transformasi

### 4. **Plan Type tidak membedakan perilaku pengguna**

* Tidak terpisah pada PCA
* Distribusi usage/spending mirip

### 5. **Segmentasi Spending lebih informatif daripada Plan Type**

* sangat mempengaruhi target offer
* dapat digunakan untuk strategi marketing

### 6. **Device Brand menjadi fitur segmentasi yang kuat**

* Brand budget → low spender
* Brand premium → high spender

### 7. **Tidak ada cluster natural yang jelas**

* Offer tidak membentuk cluster kuat di PCA/UMAP
  → classification lebih sulit, perlu fitur kuat

---

# 13. Business Impact

* **Personalization Opportunity:** 60% pelanggan masih diberi General Offer.
* **Upsell Potential:** High spender dengan usage tinggi → target Data Booster & Device Upgrade.
* **Retention Strategy:** Pelanggan dengan complaint_count tinggi → butuh intervensi.
* **Device-based Marketing:**

  * Apple/Huawei → lebih cocok campaign premium
  * Realme/Xiaomi → lebih cocok basic/general offer

---

# 14. Recommendations

### Modeling

* Gunakan LightGBM / CatBoost
* Tangani class imbalance
* Lakukan log-transform untuk spending & data usage

### Feature Engineering

* Tambahkan cost_per_gb
* Tambahkan engagement_score
* Pertimbangkan interaction terms

### Experimentation

* Targeted offer berdasarkan brand segmentation
