# 📚 Dokumentasi Preprocessing Data

## Telco Recommendation System - Data Preprocessing Pipeline

---

## 📋 Overview

Dokumentasi ini menjelaskan proses preprocessing data lengkap untuk sistem rekomendasi telco, mulai dari raw data hingga data siap untuk modeling. Pipeline ini dirancang khusus untuk menangani **imbalanced multi-class classification** dengan 9 kelas target **TANPA feature engineering**.

### Dataset Information

- **Source**: `data/raw/data_capstone.csv`
- **Total Records**: 10,000 baris (9,780 setelah cleaning)
- **Features**: 11 kolom + 1 target (original features only)
- **Target Classes**: 9 kategori offer
- **Imbalance Ratio**: 89.26:1 (sebelum SMOTE)

---

## 🎯 Tujuan Preprocessing

1. ✅ Membersihkan data dari missing values, duplicates, dan outliers
2. ✅ Menghilangkan nilai negatif yang tidak valid secara bisnis
3. ✅ Encoding dan scaling untuk transformasi data
4. ✅ **Mengatasi imbalanced data dengan SMOTE**
5. ✅ Mempersiapkan data untuk model machine learning

---

## 📊 Pipeline Preprocessing

### **STEP 1: Loading & Eksplorasi Data**

#### Deskripsi

Load data dari file CSV dan melakukan eksplorasi awal untuk memahami karakteristik data.

#### Kolom Data

| Kolom               | Tipe    | Deskripsi                          |
| ------------------- | ------- | ---------------------------------- |
| `customer_id`       | object  | ID unik pelanggan                  |
| `plan_type`         | object  | Tipe paket (Prepaid/Postpaid)      |
| `device_brand`      | object  | Brand perangkat                    |
| `avg_data_usage_gb` | float64 | Rata-rata penggunaan data (GB)     |
| `pct_video_usage`   | float64 | Persentase penggunaan video (0-1)  |
| `avg_call_duration` | float64 | Rata-rata durasi panggilan (menit) |
| `sms_freq`          | int64   | Frekuensi SMS                      |
| `monthly_spend`     | float64 | Pengeluaran bulanan (Rupiah)       |
| `topup_freq`        | int64   | Frekuensi top-up                   |
| `travel_score`      | float64 | Skor perjalanan (0-1)              |
| `complaint_count`   | int64   | Jumlah komplain                    |
| `target_offer`      | object  | Target rekomendasi (9 kelas)       |

#### Output

- Total baris: 10,000
- Total kolom: 12

---

### **STEP 2: Handling Missing Values**

#### Strategi

- **Jika missing < 5%**: Fill dengan median (numerik) atau mode (kategorikal)
- **Jika missing > 5%**: Drop kolom

#### Hasil

```
✓ Tidak ada missing values ditemukan
```

---

### **STEP 3: Handling Duplicates**

#### Proses

- Check duplikasi berdasarkan semua kolom
- Check duplikasi `customer_id`
- Hapus baris duplikat jika ditemukan

#### Hasil

```
✓ Tidak ada data duplikat ditemukan
```

---

### **STEP 4a: Removing Negative Values** ⭐

#### Deskripsi

**Langkah krusial** untuk menghilangkan nilai negatif pada kolom numerik yang tidak valid secara bisnis logic (contoh: monthly_spend tidak boleh negatif).

#### Proses

```python
# Deteksi semua kolom numerik
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

# Hapus baris dengan nilai negatif
df = df[~(df[numeric_cols] < 0).any(axis=1)]
```

#### Hasil

- Baris dengan nilai negatif: **220 baris**
- Baris setelah cleaning: **9,780 baris**
- Persentase dihapus: **2.2%**

#### Kolom yang Terpengaruh

- `avg_call_duration`: Beberapa nilai negatif (error data collection)

---

### **STEP 4b: Handling Outliers (IQR Method)**

#### Metode: Winsorization

Menggunakan metode IQR (Interquartile Range) dengan **capping** (bukan penghapusan).

#### Formula

```
Q1 = Kuartil 1 (25%)
Q3 = Kuartil 3 (75%)
IQR = Q3 - Q1
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

#### Proses

- Deteksi outliers di luar [Lower Bound, Upper Bound]
- **Cap** nilai outlier ke batas terdekat (bukan hapus)
- Preserve data size

#### Hasil per Kolom

| Kolom               | Outliers Detected | Action |
| ------------------- | ----------------- | ------ |
| `avg_data_usage_gb` | 248 (2.5%)        | Capped |
| `avg_call_duration` | 312 (3.2%)        | Capped |
| `sms_freq`          | 189 (1.9%)        | Capped |
| `monthly_spend`     | 276 (2.8%)        | Capped |
| `topup_freq`        | 198 (2.0%)        | Capped |

---

### **STEP 5: Encoding Categorical Variables**

#### Proses

##### 5.1 Label Encoding untuk Target

```python
from sklearn.preprocessing import LabelEncoder

le_target = LabelEncoder()
target_encoded = le_target.fit_transform(target)
```

**Target Mapping:**

| Class | Encoded Value |
|-------|---------------|
| Data Booster | 0 |
| Device Upgrade Offer | 1 |
| Family Plan Offer | 2 |
| General Offer | 3 |
| Retention Offer | 4 |
| Roaming Pass | 5 |
| Streaming Partner Pack | 6 |
| Top-up Promo | 7 |
| Voice Bundle | 8 |

##### 5.2 One-Hot Encoding untuk Features

```python
df_encoded = pd.get_dummies(df_encoded, columns=categorical_cols, drop_first=True)
```

**Kolom yang di-encode:**

- `plan_type`: 2 unique values → 1 dummy variable
- `device_brand`: 7 unique values → 6 dummy variables

#### Hasil

- **Features sebelum encoding**: 11 (setelah drop customer_id & target)
- **Features setelah encoding**: 16 features

---

### **STEP 6: Feature Scaling**

#### Metode: StandardScaler

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_encoded)
```

#### Formula

```
X_scaled = (X - mean) / std
```

#### Tujuan

- Normalisasi semua fitur ke skala yang sama (mean=0, std=1)
- Mencegah fitur dengan range besar mendominasi model
- Improve konvergensi algoritma ML

#### Hasil

- Semua fitur memiliki mean ≈ 0
- Semua fitur memiliki std ≈ 1
- Total features: 16

---

### **STEP 7: Train-Test Split**

#### Konfigurasi

```python
X_train, X_test, y_train, y_test = train_test_split(
    df_scaled,
    target_encoded,
    test_size=0.2,      # 20% untuk testing
    random_state=42,     # Reproducibility
    stratify=target_encoded  # Maintain class proportion
)
```

#### Hasil Split

| Set      | Samples | Percentage |
| -------- | ------- | ---------- |
| Training | 7,824   | 80%        |
| Testing  | 1,956   | 20%        |

#### Distribusi Target (Sebelum SMOTE)

**Training Set:**

| Target Offer | Count | Percentage |
|-------------|-------|------------|
| General Offer | 4,856 | 60.7% |
| Device Upgrade Offer | 1,202 | 15.0% |
| Data Booster | 638 | 8.0% |
| Retention Offer | 609 | 7.6% |
| Top-up Promo | 296 | 3.7% |
| Streaming Partner Pack | 206 | 2.6% |
| Roaming Pass | 74 | 0.9% |
| Family Plan Offer | 65 | 0.8% |
| Voice Bundle | 54 | 0.7% |

**Testing Set:**

| Target Offer | Count | Percentage |
|-------------|-------|------------|
| General Offer | 1,214 | 60.7% |
| Device Upgrade Offer | 300 | 15.0% |
| Data Booster | 159 | 8.0% |
| Retention Offer | 152 | 7.6% |
| Top-up Promo | 74 | 3.7% |
| Streaming Partner Pack | 52 | 2.6% |
| Roaming Pass | 19 | 0.9% |
| Family Plan Offer | 16 | 0.8% |
| Voice Bundle | 14 | 0.7% |

#### ⚠️ Problem Identified

**Imbalance Ratio: 89.26:1** (General Offer vs Voice Bundle)

- Kelas mayoritas mendominasi 60.7%
- 3 kelas minoritas < 1% dari total data
- **BUTUH BALANCING!** → SMOTE

---

### **STEP 7.5: Handle Imbalanced Data dengan SMOTE** ⭐

#### Mengapa SMOTE?

**Masalah Imbalanced Data:**

1. ❌ Model bias ke kelas mayoritas
2. ❌ Poor performance pada kelas minoritas
3. ❌ High accuracy tapi misleading
4. ❌ Tidak bisa belajar pattern kelas minoritas

**Solusi: SMOTE (Synthetic Minority Over-sampling Technique)**

#### Cara Kerja SMOTE

```
1. Untuk setiap sampel di kelas minoritas:
   - Cari k nearest neighbors (default k=5)
   - Pilih salah satu neighbor secara random
   - Buat synthetic sample di antara kedua points

2. Ulangi sampai semua kelas balanced
```

#### Implementasi

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
```

#### Hasil SMOTE

**Distribusi Setelah SMOTE:**

| Target Offer | Before SMOTE | After SMOTE | Synthetic Added |
|-------------|--------------|-------------|-----------------|
| General Offer | 4,856 | 4,856 | 0 |
| Device Upgrade Offer | 1,202 | 4,856 | +3,654 |
| Data Booster | 638 | 4,856 | +4,218 |
| Retention Offer | 609 | 4,856 | +4,247 |
| Top-up Promo | 296 | 4,856 | +4,560 |
| Streaming Partner Pack | 206 | 4,856 | +4,650 |
| Roaming Pass | 74 | 4,856 | +4,782 |
| Family Plan Offer | 65 | 4,856 | +4,791 |
| Voice Bundle | 54 | 4,856 | +4,802 |

**Summary:**

- **Training samples (before)**: 7,824
- **Training samples (after)**: 43,704
- **Synthetic samples created**: 35,880
- **New imbalance ratio**: 1:1 ✓ (PERFECTLY BALANCED)
- **Test set**: Tetap 1,956 (TIDAK diubah)

#### ⚠️ Catatan Penting

1. **SMOTE hanya diterapkan pada training set**

   - Test set tetap menggunakan data original
   - Untuk evaluasi yang fair dan realistic

2. **K-Neighbors = 5**

   - Untuk kelas dengan < 5 samples, otomatis adjust
   - Mencegah overfitting

3. **Random State = 42**
   - Untuk reproducibility
   - Hasil konsisten setiap run

---

### **STEP 8: Save Processed Data**

#### Files yang Disimpan

##### 1. **Numpy Arrays**

```
data/processed/
├── X_train.npy          # Training features (BALANCED - 43,704 samples)
├── y_train.npy          # Training labels (BALANCED - 43,704 samples)
├── X_test.npy           # Testing features (ORIGINAL - 1,956 samples)
└── y_test.npy           # Testing labels (ORIGINAL - 1,956 samples)
```

##### 2. **Pickle Objects**

```
data/processed/
├── scaler.pkl           # StandardScaler object untuk production
├── label_encoder.pkl    # LabelEncoder untuk decode predictions
├── feature_names.pkl    # List nama fitur (16 features)
└── target_mapping.pkl   # Dictionary mapping target classes
```

##### 3. **CSV File**

```
data/processed/
└── processed_data.csv   # Complete processed dataframe (untuk analisis)
```

#### Cara Load Processed Data

```python
import numpy as np
import pickle

# Load training data (sudah balanced dengan SMOTE)
X_train = np.load('data/processed/X_train.npy')
y_train = np.load('data/processed/y_train.npy')

# Load testing data (original)
X_test = np.load('data/processed/X_test.npy')
y_test = np.load('data/processed/y_test.npy')

# Load artifacts
with open('data/processed/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('data/processed/label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

with open('data/processed/feature_names.pkl', 'rb') as f:
    feature_names = pickle.load(f)

print(f"Training samples: {len(y_train):,}")
print(f"Testing samples: {len(y_test):,}")
print(f"Features: {len(feature_names)}")
```

---

## 📈 Summary Preprocessing

### Data Transformation Journey

```
RAW DATA (10,000 baris, 12 kolom)
    ↓
Handle Missing Values (0 changes)
    ↓
Handle Duplicates (0 changes)
    ↓
Remove Negative Values (-220 baris)
    ↓
Handle Outliers (1,223 values capped)
    ↓
CLEAN DATA (9,780 baris, 12 kolom)
    ↓
Encoding Categorical (+5 dummy variables)
    ↓
ENCODED DATA (9,780 baris, 16 features)
    ↓
Feature Scaling (standardization)
    ↓
SCALED DATA (9,780 baris, 16 features)
    ↓
Train-Test Split (80/20)
    ↓
TRAIN: 7,824 baris | TEST: 1,956 baris
    ↓
SMOTE Balancing (training only)
    ↓
FINAL TRAIN: 43,704 baris (BALANCED) ✓
FINAL TEST: 1,956 baris (ORIGINAL) ✓
```

### Key Metrics

| Metric                             | Value                          |
| ---------------------------------- | ------------------------------ |
| **Original Data Size**             | 10,000 baris                   |
| **After Cleaning**                 | 9,780 baris                    |
| **Data Loss**                      | 220 baris (2.2%)               |
| **Original Features**              | 12                             |
| **Final Features**                 | 16 (tanpa feature engineering) |
| **Training Samples (Original)**    | 7,824                          |
| **Training Samples (After SMOTE)** | 43,704                         |
| **Testing Samples**                | 1,956                          |
| **Imbalance Ratio (Before)**       | 89.26:1 ⚠️                     |
| **Imbalance Ratio (After)**        | 1:1 ✓                          |

---

## 🎯 Best Practices Applied

### ✅ Data Quality

- [x] Remove invalid negative values
- [x] Handle outliers appropriately (capping, not deletion)
- [x] Check for missing values and duplicates
- [x] Maintain data integrity throughout pipeline

### ✅ Preprocessing

- [x] Proper encoding (Label + One-Hot)
- [x] Standardization for numeric features
- [x] Stratified train-test split
- [x] **NO feature engineering** - menggunakan fitur original saja

### ✅ Imbalanced Data Handling

- [x] SMOTE only on training set
- [x] Perfect balance achieved (1:1 ratio)
- [x] Test set kept original for fair evaluation

### ✅ Production Ready

- [x] Save all artifacts (scaler, encoder)
- [x] Reproducible results (random_state=42)
- [x] Well-documented process
- [x] Easy to load and use in production

---

## 🚀 Next Steps - Modeling

### Recommended Algorithms

#### 1. **Random Forest Classifier**

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=10,
    random_state=42
)
```

- ✅ Handle multi-class well
- ✅ Feature importance available
- ✅ Robust to outliers

#### 2. **XGBoost**

```python
import xgboost as xgb

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=10,
    learning_rate=0.1,
    random_state=42
)
```

- ✅ State-of-the-art performance
- ✅ Built-in regularization
- ✅ Fast training

#### 3. **LightGBM**

```python
import lightgbm as lgb

model = lgb.LGBMClassifier(
    n_estimators=200,
    max_depth=10,
    learning_rate=0.1,
    random_state=42
)
```

- ✅ Faster than XGBoost
- ✅ Lower memory usage
- ✅ Good with categorical features

### Evaluation Metrics

**⚠️ JANGAN hanya pakai Accuracy!**

Untuk imbalanced data (walaupun sudah di-SMOTE), gunakan:

1. **F1-Score (Weighted/Macro)**

   ```python
   from sklearn.metrics import f1_score
   f1 = f1_score(y_test, y_pred, average='weighted')
   ```

2. **Precision & Recall per Class**

   ```python
   from sklearn.metrics import classification_report
   print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
   ```

3. **Confusion Matrix**

   ```python
   from sklearn.metrics import confusion_matrix
   cm = confusion_matrix(y_test, y_pred)
   ```

4. **ROC-AUC (Multi-class)**

   ```python
   from sklearn.metrics import roc_auc_score
   auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
   ```

---

## 📝 Changelog

### Version 1.1 (November 2025)

- ✅ **REMOVED** Feature Engineering step
- ✅ Simplified pipeline menggunakan fitur original
- ✅ Total features: 16 (vs 24 di versi sebelumnya)
- ✅ Lebih cepat dan efficient

### Version 1.0 (November 2025)

- ✅ Initial preprocessing pipeline
- ✅ Handle missing values, duplicates, outliers
- ✅ Remove negative values
- ✅ Feature engineering (6 new features) - DEPRECATED
- ✅ Encoding & scaling
- ✅ SMOTE implementation for imbalanced data
- ✅ Complete documentation

---

## 👥 Contributors

**Telco System Recommendation Team**

- Data Science Team
- ML Engineering Team

---

## 📞 Contact & Support

Untuk pertanyaan atau issue terkait preprocessing:

1. Check notebook: `notebook/preposesingData.ipynb`
2. Review code: `src/preprocessing.py`
3. Contact: Data Science Team

---

**Last Updated:** November 14, 2025  
**Status:** ✅ Production Ready  
**Version:** 1.1 (No Feature Engineering)
