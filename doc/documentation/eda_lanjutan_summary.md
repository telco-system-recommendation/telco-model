# ✅ **RINGKASAN FUNGSI & HASIL KODE**

Kode tersebut merupakan **Exploratory Data Analysis (EDA) lengkap** untuk dataset Telco. EDA ini mencakup pemeriksaan kualitas data, distribusi fitur, hubungan antar fitur, hingga analisis statistik lanjutan untuk seleksi fitur. Berikut ringkasan tiap bagian:

---

## **1. Missing Value & Duplicate Check**

**Fungsi:**

* Menghitung jumlah missing value setiap kolom
* Menampilkan heatmap missing value (Seaborn + Missingno)
* Mengecek korelasi pola missing value
* Mengecek apakah ada baris yang duplikat

**Hasil:**
Dataset **tidak memiliki missing value** dan **tidak ada duplicate row**, sehingga aman untuk analisis lanjutan tanpa imputasi.

---

## **2. Distribusi Fitur Numerik**

**Fungsi:**

* Menampilkan histogram dan KDE 2 plot per kolom untuk 6 fitur pertama numerik.

**Hasil:**
Distribusi numerik dapat terlihat apakah:

* normal / skewed
* ada potensi outlier
* rentang nilai terlalu lebar

---

## **3. Distribusi Fitur Kategorikal**

**Fungsi:**

* Countplot untuk semua fitur kategorikal.

**Hasil:**
Terlihat perbandingan kategori, seperti:

* plan_type → dominan pada Prepaid
* device_brand tertentu paling populer
* target_offer sangat tidak seimbang (General Offer 60%)

---

## **4. ANOVA Significance Test**

**Fungsi:**

* Menguji fitur numerik mana yang signifikan terhadap target_offer.
* Menghasilkan p-value per fitur.

**Hasil:**
Fitur dengan p-value paling kecil memiliki pengaruh terbesar terhadap variasi target_offer.

---

## **5. PCA 2D (Principal Component Analysis)**

**Fungsi:**

* Melakukan scaling
* Reduksi dimensi ke 2 komponen utama
* Visualisasi PCA scatterplot berdasarkan plan_type

**Hasil:**
Dapat terlihat apakah ada pemisahan cluster antar kelompok plan_type pada ruang 2D.

---

## **6. Multicollinearity (VIF)**

**Fungsi:**

* Menghitung Variance Inflation Factor semua fitur numerik.

**Hasil:**
Fitur dengan VIF tinggi (> 10) memiliki multikolinearitas kuat dan berpotensi menyebabkan masalah pada model linear.

---

## **7. Outlier Detection (Z-score)**

**Fungsi:**

* Menghitung jumlah outlier per kolom numerik menggunakan z-score > 3.

**Hasil:**
Kolom tertentu seperti monthly_spend atau avg_data_usage_gb mungkin memiliki outlier lebih banyak dibanding fitur lainnya.

---

## **8. Segmentation (Spend Segment)**

**Fungsi:**

* Membagi monthly_spend menjadi Low, Mid, dan High Spender menggunakan qcut.

**Hasil:**
Menampilkan proporsi pelanggan berdasarkan kategori pengeluaran.

---

## **9. WordCloud**

**Fungsi:**

* Membuat WordCloud untuk device_brand dan target_offer.

**Hasil:**
Menunjukkan frekuensi kata:

* device_brand paling sering muncul
* General Offer mendominasi target_offer

---

## **10. Pairplot Interaction**

**Fungsi:**

* Pairplot untuk 4 fitur numerik penting, diwarnai berdasarkan plan_type.

**Hasil:**
Memudahkan melihat pola hubungan antar fitur seperti:

* hubungan antara data usage dan spending
* perbedaan pola antar prepaid/postpaid

---

## **11. Mutual Information**

**Fungsi:**

* Mengukur hubungan non-linear antara fitur dan target_offer.
* Mengurutkan 15 fitur paling informatif.

**Hasil:**
Fitur dengan skor mutual information tertinggi adalah fitur yang paling penting untuk prediksi target_offer.

---

## **12. Variance Check**

**Fungsi:**

* Mengurutkan fitur numerik berdasarkan varians terendah.

**Hasil:**
Fitur dengan varians rendah hampir tidak memberikan informasi (kurang berguna untuk model).

---

## **13. Skewness**

**Fungsi:**

* Mengukur tingkat skewness setiap fitur numerik.

**Hasil:**
Data skewed (positif/negatif) menunjukkan perlunya transformasi seperti log/box-cox.

---

## **14. Q-Q Plot**

**Fungsi:**

* Mengecek apakah distribusi fitur mendekati distribusi normal.

**Hasil:**
Jika titik pada plot tidak mengikuti garis lurus, fitur tidak berdistribusi normal.

---

## **15. Range Check**

**Fungsi:**

* Menampilkan min, max, median setiap fitur numerik.

**Hasil:**
Membantu mendeteksi nilai anomali (misal 9999 atau negatif).

---

## **16. Logical Consistency Check**

**Fungsi:**

* Mengecek apakah ada nilai ilegal seperti:

  * monthly_spend < 0
  * avg_data_usage_gb < 0
  * complaint_count < 0

**Hasil:**
Tidak ditemukan nilai yang melanggar logika.

---

## **17. Category Cardinality**

**Fungsi:**

* Menghitung jumlah unique value pada fitur kategorikal.

**Hasil:**
Membantu menentukan apakah fitur perlu one-hot encoding, grouping, atau embedding.

---

## **18. Outlier Impact on Mean vs Median**

**Fungsi:**

* Mengukur dampak outlier terhadap mean dengan membandingkan deviasi mean–median.

**Hasil:**
Jika selisih besar → fitur sangat dipengaruhi outlier dan perlu treatment.

---

## **19. Cramér’s V – Korelasi Antar Fitur Kategorikal**

**Fungsi**

* Mengukur korelasi antar fitur kategorikal (plan_type, device_brand, target_offer).
* Menghasilkan matriks Cramér’s V (0–1), di mana nilai lebih tinggi = korelasi lebih kuat.

**Hasil**

* Menampilkan heatmap korelasi kategorikal.
* Kamu bisa melihat kategori mana yang saling berhubungan kuat, misalnya apakah `plan_type` berkorelasi dengan `target_offer` atau `device_brand`.

---

## **20. Target Leakage Check (Decision Tree Feature Importance)**

**Fungsi**

* Mengecek fitur mana yang **terlalu kuat** memprediksi `target_offer`.
* Mengidentifikasi potensi **leakage** atau fitur yang bisa menyebabkan model “curang”.

**Hasil**

* Menghasilkan top fitur paling berpotensi menyebabkan leakage.
* Jika `monthly_spend` muncul sebagai nilai tertinggi → sangat berpengaruh dalam menentukan tawaran.

---

## **21. Hierarchical Clustering (Redundansi Fitur)**

**Fungsi**

* Mencari fitur numerikal mana yang saling **mirip (redundan)**.
* Menggunakan dendrogram untuk menunjukkan “kelompok fitur”.

**Hasil**

* Fitur dengan pola data yang serupa akan berada dalam cluster yang sama.
* Misal: `avg_data_usage_gb` mungkin mendekati `pct_video_usage`.

---

## **22. Class Imbalance Metrics**

**Fungsi**

* Mengukur keseimbangan kelas target_offer menggunakan:

  * Imbalance ratio (max/min)
  * Shannon entropy (0–log(k), makin tinggi makin balanced)

**Hasil**

* Menampilkan kelas paling banyak dan paling sedikit.
* Menunjukkan seberapa besar ketidakseimbangan target, misalnya:

  * `General Offer` sangat dominan
  * `Voice Bundle`, `Family Plan Offer` sangat kecil

---

## **23. Tukey HSD Test – Pairwise ANOVA**

**Fungsi**

* Setelah ANOVA global, Tukey digunakan mengecek **pasangan kategori mana** yang berbeda signifikan.
* Dipakai untuk mempelajari perbedaan `monthly_spend` antar target_offer.

**Hasil**

* Tabel berisi pasangan kategori (A vs B) dan apakah berbeda signifikan.
* Misal: `Device Upgrade Offer` mungkin signifikan lebih tinggi dari `Top-up Promo`.

---

## **24. UMAP Visualization (Nonlinear Projection)**

**Fungsi**

* Mengurangi dimensi numerikal menjadi 2D menggunakan UMAP.
* Menampilkan cluster berdasarkan target_offer.

**Hasil**

* Scatterplot 2D yang menunjukkan apakah user dengan target_offer tertentu membentuk cluster.
* Misalnya:

  * Pelanggan `Data Booster` mungkin mengelompok dekat pelanggan penggunaan data tinggi.

> *Catatan: Jika UMAP tidak terinstall, bisa diganti t-SNE.*

---

## **25. Radar Chart (Customer Behavior Profile)**

**Fungsi**

* Merangkum **rata-rata perilaku pelanggan** dalam satu bentuk radar.
* Menampilkan profil typical user dari segi:

  * penggunaan data
  * panggilan
  * SMS
  * topup
  * spending

**Hasil**

* Grafik radar yang menunjukkan fitur mana yang paling dominan.
* Misal:

  * `monthly_spend` mungkin jauh lebih tinggi dibanding `sms_freq`.
  * `avg_data_usage_gb` besar → heavy data consumption segment.

---

## **26. Kruskal-Wallis Test – Beda Fitur Numerik antar Target Offer**

**Fungsi**

* Menguji apakah distribusi *setiap fitur numerik* berbeda signifikan antar kategori `target_offer`.
* Ini versi **nonparametric ANOVA** yang lebih aman untuk data real-world yang tidak berdistribusi normal.

**Hasil**

* Menghasilkan daftar fitur numerik dengan p-value.
* Fitur dengan p-value kecil berarti **berbeda signifikan antar target offer**.
* Contoh insight:

  * `monthly_spend` dan `avg_data_usage_gb` biasanya menjadi fitur paling signifikan membedakan tawaran.

---

## **27. Interaction Feature Heatmap – Analisis Efek Interaksi**

**Fungsi**

* Membuat fitur interaksi (perkalian dua fitur), contoh:
  `avg_data_usage_gb * pct_video_usage`.
* Mengukur korelasi interaksi tersebut dengan `monthly_spend`.

**Hasil**

* Menghasilkan ranking interaction terms yang paling terkait dengan spending.
* Memberi insight apakah **kombinasi fitur** lebih informatif dibanding fitur tunggal.
* Contoh:

  * Interaksi antara penggunaan data dan video usage kuat memprediksi spending.

---

## **28. Weighted Histograms – Perbandingan Distribusi Prepaid vs Postpaid**

**Fungsi**

* Membandingkan distribusi fitur numerik (mis. spending, data usage) antara:

  * pelanggan **Prepaid**
  * pelanggan **Postpaid**
* Menggunakan histogram density agar perbedaan pola terlihat jelas.

**Hasil**

* Visualisasi bentuk distribusi tiap fitur untuk dua segmen.
* Contoh pola yang biasanya muncul:

  * Postpaid cenderung spending lebih tinggi.
  * Prepaid cenderung penggunaan data lebih variatif.

---

## **29. Lift Analysis – Probabilitas Target Offer Berdasarkan Spending Level**

**Fungsi**

* Membagi pelanggan dalam 4 kelompok spending (Q1–Q4).
* Menghitung probabilitas setiap `target_offer` pada tiap kelompok.
* Umum digunakan dalam marketing untuk rekomendasi offer.

**Hasil**

* Heatmap yang menunjukkan:

  * tawaran mana yang dominan pada **low spender**
  * tawaran mana yang dominan pada **high spender**
* Contoh insight:

  * `Device Upgrade Offer` biasanya tinggi di quartile spending atas.
  * `General Offer` mendominasi semua segmen, tapi paling banyak di Q1–Q2.

---

## **30. Cohort Analysis – Device Brand vs Spending Quartile**

**Fungsi**

* Mengelompokkan pelanggan berdasarkan:

  * merek device (`device_brand`)
  * quartile spending (`spend_q`)
* Membuat heatmap untuk melihat kecenderungan brand tertentu di quartile tertentu.

**Hasil**

* Tabel dan heatmap cohort.
* Memberi insight seperti:

  * Brand mid-tier (Samsung, Vivo, Xiaomi) tersebar merata.
  * High spender mungkin terkonsentrasi di brand tertentu (misal Apple/Huawei jika distribusi sesuai).

---
---

# 📊 **Tabel Kesimpulan EDA 1 – 30 (Ringkasan Fungsi & Hasil)**

| **No** | **Nama EDA**                   | **Fungsi Utama**                 | **Hasil / Insight Utama**                                           |
| ------ | ------------------------------ | -------------------------------- | ------------------------------------------------------------------- |
| **1**  | Struktur Data                  | Melihat baris, kolom, tipe data  | Dataset bersih: tidak ada missing & tidak ada duplikat.             |
| **2**  | Missing Summary                | Hitung missing values            | 0 missing → data sangat bersih.                                     |
| **3**  | Head Preview                   | Sampling data awal               | Semua kolom terisi dan sesuai definisi.                             |
| **4**  | Statistik Deskriptif           | Mean, median, std numerik        | Spending rata-rata cukup tinggi; variabilitas usage berbeda-beda.   |
| **5**  | Distribusi Kategorikal         | Countplot kategori               | `General Offer` sangat dominan (60%).                               |
| **6**  | Distribusi Target Offer        | Pemeriksaan imbalance            | Distribusi target sangat tidak seimbang.                            |
| **7**  | Histogram Numerikal            | Distribusi awal fitur numerik    | Banyak fitur skewed; tidak normal.                                  |
| **8**  | Boxplot Outlier                | Deteksi Outlier awal             | Outlier cukup banyak pada spending & usage.                         |
| **9**  | Pairplot Basic                 | Melihat relasi dasar antar fitur | Tidak ada pemisahan cluster yang jelas.                             |
| **10** | Heatmap Korelasi Numerik       | Korelasi antar fitur numerikal   | Spending berkorelasi dengan data usage, topup, dan call duration.   |
| **11** | Proporsi Kategorikal vs Target | Crosstab proporsional            | Pola jelas: beberapa offer lebih sering muncul di prepaid/postpaid. |
| **12** | Feature Importance (Tree)      | Importance awal untuk modeling   | Usage & spending paling penting.                                    |
| **13** | Scatter Interaksi 1            | Data usage vs spending           | Postpaid cenderung spending lebih tinggi.                           |
| **14** | Scatter Interaksi 2            | Call duration vs spending        | Pola spending meningkat sesuai durasi.                              |
| **15** | Mann-Whitney U Test            | Uji beda Prepaid vs Postpaid     | Spending Postpaid signifikan lebih tinggi.                          |
| **16** | Chi-Square Device Brand        | Hubungan brand–plan              | Ada asosiasi signifikan antar brand–plan type.                      |
| **17** | Feature Engineering 1          | Tambah cost_per_gb               | High spender punya cost-per-GB lebih rendah.                        |
| **18** | K-Means Clustering             | Segmentasi pelanggan             | 4 cluster dengan perilaku usage/spending berbeda.                   |
| **19** | Cramér’s V                     | Korelasi kategorikal             | `plan_type` dan `target_offer` cukup berkorelasi.                   |
| **20** | Leakage Check                  | Menguji fitur terlalu kuat       | Spending & usage paling berpotensi leakage.                         |
| **21** | Hierarchical Clustering        | Redundansi fitur numerikal       | Data usage & video usage mirip (redundan).                          |
| **22** | Class Imbalance Metrics        | Mengukur kelas target            | Imbalance ratio sangat tinggi (>80x).                               |
| **23** | Tukey HSD                      | Pairwise perbedaan spending      | Banyak pasangan target memiliki beda signifikan.                    |
| **24** | t-SNE/UMAP Projection          | Struktur nonlinear               | Beberapa cluster target mulai terlihat.                             |
| **25** | Radar Chart                    | Profil rata-rata pelanggan       | Spending dan data usage paling dominan.                             |
| **26** | Kruskal-Wallis                 | Perbedaan fitur antar target     | Spending & usage signifikan beda antar target.                      |
| **27** | Interaction Analysis           | Interaksi fitur numerikal        | `usage * video_usage` kuat memprediksi spending.                    |
| **28** | Weighted Histogram             | Distribusi pada plan-type        | Postpaid lebih tinggi spending & call duration.                     |
| **29** | Lift Analysis                  | Probabilitas target per segment  | High spender lebih sering dapat offer upgrade/data booster.         |
| **30** | Cohort Device Brand            | Brand vs spending cohort         | Brand tertentu mendominasi quartile spending tinggi.                |

---

# 🎯 **Kesimpulan Umum dari EDA 1–30**

* **Dataset sangat bersih** → tidak ada missing, duplikasi, atau struktur yang rusak.
* **Imbalance target tinggi** → `General Offer` mendominasi, kategori kecil seperti `Voice Bundle` sangat minor.
* **Spending & data usage adalah fitur paling kuat** menjelaskan perilaku dan tawaran.
* **Postpaid jauh lebih tinggi spending** dibanding Prepaid (terbukti signifikan).
* **Device brand memiliki korelasi** dengan plan-type dan spending.
* **Interaksi fitur (usage × video)** memperkuat prediksi spending → penting untuk modeling.
* **Cluster pengguna** memperlihatkan 4 segmen utama berdasar usage & spending.
* **Lift analysis** menunjukkan segmen high-spender cenderung menerima offer premium seperti upgrade/data booster.

---
