# 📊 Dokumentasi Sistem Rekomendasi Telco - Cold Start & Berkelanjutan

## 📋 Daftar Isi

1. [Overview Sistem](#overview-sistem)
2. [Struktur Database](#struktur-database)
3. [Fitur Model](#fitur-model)
4. [Flow Cold Start](#flow-cold-start)
5. [Flow Rekomendasi Berkelanjutan](#flow-rekomendasi-berkelanjutan)
6. [Implementasi Backend](#implementasi-backend)
7. [Update Strategy](#update-strategy)

---

## 🎯 Overview Sistem

Sistem rekomendasi ini menggunakan **hybrid approach** yang menggabungkan:

- **Cold Start Profile**: Data profil user yang diisi sekali dan disimpan permanen
- **Behavioral Features**: Data penggunaan yang dihitung otomatis secara real-time

### Tujuan

Memberikan rekomendasi paket telco yang personal dan akurat untuk setiap user berdasarkan profil dan perilaku penggunaan mereka.

### Karakteristik

- ✅ **Cold Start Friendly**: User baru bisa langsung dapat rekomendasi
- 🔄 **Real-time Updates**: Rekomendasi selalu fresh berdasarkan data terbaru
- 📈 **Self-Learning**: Makin akurat seiring user makin aktif
- 🚀 **Scalable**: Efficient query dan caching strategy

---

## 🗄️ Struktur Database

### Tabel: `users`

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    full_name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,

    -- Status & Security
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP,

    INDEX idx_email (email),
    INDEX idx_phone (phone)
);


CREATE TABLE user_profiles (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,

    -- ✅ PROFIL PERMANEN (Cold Start)
    plan_type VARCHAR(20),
    device_brand VARCHAR(50),
    pct_video_usage FLOAT DEFAULT 0,
    avg_call_duration FLOAT DEFAULT 0,
    travel_score FLOAT DEFAULT 0,

    -- Metadata Cold Start
    is_profiled BOOLEAN DEFAULT FALSE,
    profiled_at TIMESTAMP,

    -- 🔄 BEHAVIORAL FEATURES (Real-time)
    avg_data_usage_gb FLOAT DEFAULT 0,
    monthly_spend FLOAT DEFAULT 0,
    topup_freq INT DEFAULT 0,
    complaint_count INT DEFAULT 0,
    last_features_updated TIMESTAMP,

    -- Cache Rekomendasi
    last_recommendation VARCHAR(100),
    last_recommendation_at TIMESTAMP,
    last_recommendation_confidence FLOAT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_profiled (is_profiled)
);
```

### Tabel: `transactions`

```sql
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,

    -- Detail Paket
    package_id INT,
    package_name VARCHAR(255) NOT NULL,       -- Nama paket yang dibeli
    package_gb FLOAT NOT NULL,                -- Jumlah GB dalam paket
    package_validity_days INT,                -- Masa aktif paket (hari)

    -- Billing
    amount FLOAT NOT NULL,                    -- Harga paket
    payment_method VARCHAR(50),               -- 'credit_card', 'ewallet', 'transfer', dll

    -- Status
    status VARCHAR(20) NOT NULL,              -- 'pending', 'completed', 'failed', 'cancelled'
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_user_date (user_id, transaction_date)
);
```

### Tabel: `complaints`

```sql
CREATE TABLE complaints (
    complaint_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,

    -- Detail Komplain
    subject VARCHAR(255) NOT NULL,            -- Judul komplain
    description TEXT,                         -- Deskripsi lengkap
    category VARCHAR(50),                     -- 'network', 'billing', 'service', dll
    priority VARCHAR(20) DEFAULT 'normal',    -- 'low', 'normal', 'high', 'urgent'

    -- Status
    status VARCHAR(20) DEFAULT 'open',        -- 'open', 'in_progress', 'resolved', 'closed'
    resolution TEXT,                          -- Solusi/penyelesaian

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_user_date (user_id, created_at)
);
```

### Tabel: `packages` (Optional - Master Data)

```sql
CREATE TABLE packages (
    package_id INT PRIMARY KEY AUTO_INCREMENT,
    package_name VARCHAR(255) NOT NULL,
    package_type VARCHAR(50),                 -- 'data', 'voice', 'combo', dll
    data_gb FLOAT,
    voice_minutes INT,
    sms_count INT,
    validity_days INT,
    price FLOAT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_package_type (package_type),
    INDEX idx_is_active (is_active)
);
```

---

## 🎯 Fitur Model

### Total Fitur: 8 fitur utama + encoding categorical

| #   | Nama Fitur          | Tipe          | Source                 | Update Frequency |
| --- | ------------------- | ------------- | ---------------------- | ---------------- |
| 1   | `plan_type`         | Categorical   | Cold Start (Permanen)  | Manual edit      |
| 2   | `device_brand`      | Categorical   | Cold Start (Permanen)  | Manual edit      |
| 3   | `pct_video_usage`   | Numeric (0-1) | Cold Start (Permanen)  | Manual edit      |
| 4   | `avg_call_duration` | Numeric       | Cold Start (Permanen)  | Manual edit      |
| 5   | `travel_score`      | Numeric (0-1) | Cold Start (Permanen)  | Manual edit      |
| 6   | `avg_data_usage_gb` | Numeric       | Behavioral (Real-time) | Setiap transaksi |
| 7   | `monthly_spend`     | Numeric       | Behavioral (Real-time) | Setiap transaksi |
| 8   | `topup_freq`        | Numeric       | Behavioral (Real-time) | Setiap transaksi |
| 9   | `complaint_count`   | Numeric       | Behavioral (Real-time) | Setiap komplain  |

### Fitur yang Dikecualikan (Tidak Dipakai)

❌ `sms_freq` - Sulit tracking, tidak relevan (SMS jarang dipakai)
❌ `avg_call_duration` - Bisa diganti dengan pertanyaan kategorikal
❌ Data lain yang memerlukan integrasi real-time dengan provider

### Setelah Encoding

```
Fitur Input = 8 fitur numerik + one-hot encoding untuk categorical
├─ plan_type → plan_type_Prepaid, plan_type_Postpaid (2 kolom)
└─ device_brand → device_brand_Samsung, device_brand_Xiaomi, ... (7 kolom)

Total input ke model = 8 + 2 + 7 = 17 fitur
```

---

## 🚀 Flow Cold Start

### Step 1: User Registration

```
User mendaftar dengan email/phone
    ↓
Redirect ke Cold Start Form
```

### Step 2: Cold Start Form (4 Pertanyaan)

```
┌─────────────────────────────────────────────────────┐
│           FORM PROFIL AWAL (Cold Start)             │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Jenis paket yang Anda minati?                   │
│     ○ Prepaid - Isi ulang kapan saja               │
│     ○ Postpaid - Bayar di akhir bulan              │
│                                                      │
│  2. Device brand yang Anda gunakan?                 │
│     [Dropdown: Samsung/Xiaomi/Oppo/Vivo/...]       │
│                                                      │
│  3. Seberapa sering Anda menonton video streaming?  │
│     ○ Tidak pernah                                  │
│     ○ Jarang (1-2 jam/minggu)                      │
│     ○ Kadang-kadang (3-5 jam/minggu)               │
│     ○ Sering (6-10 jam/minggu)                     │
│     ○ Sangat sering (>10 jam/minggu)               │
│                                                      │
│  4. Apakah Anda tertarik dengan paket telepon?      │
│     ○ Tidak, saya jarang telepon                   │
│     ○ Ya, sesekali telepon                         │
│     ○ Ya, cukup sering telepon                     │
│     ○ Ya, sangat sering telepon                    │
│                                                      │
│  5. Seberapa sering Anda bepergian?                 │
│     ○ Tidak pernah                                  │
│     ○ Jarang (1-2 kali/tahun)                      │
│     ○ Kadang (3-6 kali/tahun)                      │
│     ○ Sering (>6 kali/tahun)                       │
│                                                      │
│              [Simpan dan Lanjutkan]                 │
└─────────────────────────────────────────────────────┘
```

### Step 3: Konversi ke Database

```python
# Mapping jawaban ke nilai numerik
VIDEO_MAPPING = {
    'never': 0.0,
    'rarely': 0.15,
    'sometimes': 0.35,
    'often': 0.60,
    'always': 0.85
}

CALL_MAPPING = {
    'no': 0.0,
    'light': 3.5,
    'moderate': 8.0,
    'heavy': 15.0
}

TRAVEL_MAPPING = {
    'never': 0.0,
    'rarely': 0.2,
    'sometimes': 0.4,
    'often': 0.7
}

# Simpan ke database
user.plan_type = 'Prepaid'
user.device_brand = 'Samsung'
user.pct_video_usage = 0.60        # dari 'often'
user.avg_call_duration = 8.0       # dari 'moderate'
user.travel_score = 0.4            # dari 'sometimes'
user.is_profiled = True
user.profiled_at = datetime.now()

# Behavioral features = 0 (user baru)
user.avg_data_usage_gb = 0
user.monthly_spend = 0
user.topup_freq = 0
user.complaint_count = 0

db.session.commit()
```

### Step 4: Generate Rekomendasi Pertama

```
User dengan:
├─ Profil Cold Start (dari jawaban)
└─ Behavioral = 0 (belum ada transaksi)
    ↓
Model ML Predict
    ↓
Rekomendasi Offer Pertama
```

---

## 🔄 Flow Rekomendasi Berkelanjutan

### Setiap User Login/Buka Dashboard

```
┌──────────────────────────────────────────────────────┐
│  User Login / Buka Dashboard                         │
└──────────────┬───────────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────────┐
│  Cek: is_profiled == TRUE?                           │
├──────────────┬───────────────────────────────────────┤
│ FALSE        │ TRUE                                   │
│ ↓            │ ↓                                      │
│ Redirect     │ Hitung Behavioral Features             │
│ Cold Start   │ (Query 30 hari terakhir)              │
│              │ ├─ avg_data_usage_gb                   │
│              │ ├─ monthly_spend                       │
│              │ ├─ topup_freq                          │
│              │ └─ complaint_count                     │
└──────────────┴───────────────────┬───────────────────┘
                                   ↓
┌──────────────────────────────────────────────────────┐
│  Gabungkan Profil Permanen + Behavioral              │
│  ├─ plan_type (dari DB)                              │
│  ├─ device_brand (dari DB)                           │
│  ├─ pct_video_usage (dari DB)                        │
│  ├─ avg_call_duration (dari DB)                      │
│  ├─ travel_score (dari DB)                           │
│  ├─ avg_data_usage_gb (hitung real-time)             │
│  ├─ monthly_spend (hitung real-time)                 │
│  ├─ topup_freq (hitung real-time)                    │
│  └─ complaint_count (hitung real-time)               │
└──────────────────────────┬───────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────┐
│  Preprocessing & Prediction                          │
│  ├─ One-hot encoding categorical                     │
│  ├─ Feature scaling                                  │
│  └─ Model.predict()                                  │
└──────────────────────────┬───────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────┐
│  Update Cache & Tampilkan                            │
│  ├─ last_recommendation = "Streaming Offer"          │
│  ├─ last_recommendation_at = NOW()                   │
│  └─ last_recommendation_confidence = 0.85            │
└──────────────────────────────────────────────────────┘
```

---

## 💻 Implementasi Backend

### 1. Feature Service

```python
# services/feature_service.py
from datetime import datetime, timedelta
from models import Transaction, Complaint, User
from database import db

class FeatureService:

    @staticmethod
    def calculate_behavioral_features(user_id):
        """
        Hitung fitur behavioral dari data 30 hari terakhir
        Dipanggil setiap user login/buka dashboard
        """
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Query transaksi 30 hari terakhir
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= thirty_days_ago,
            Transaction.status == 'completed'
        ).all()

        # 1. avg_data_usage_gb: Total GB / Jumlah transaksi
        if transactions:
            total_gb = sum(t.package_gb for t in transactions)
            avg_data = round(total_gb / len(transactions), 2)
        else:
            avg_data = 0.0

        # 2. monthly_spend: Total pengeluaran
        monthly_spend = round(sum(t.amount for t in transactions), 2)

        # 3. topup_freq: Jumlah transaksi
        topup_freq = len(transactions)

        # 4. complaint_count: Jumlah komplain
        complaint_count = Complaint.query.filter(
            Complaint.user_id == user_id,
            Complaint.created_at >= thirty_days_ago
        ).count()

        return {
            'avg_data_usage_gb': avg_data,
            'monthly_spend': monthly_spend,
            'topup_freq': topup_freq,
            'complaint_count': complaint_count
        }

    @staticmethod
    def get_complete_features(user_id):
        """
        Gabungkan profil permanen + behavioral real-time
        """
        user = User.query.get(user_id)

        if not user:
            raise Exception(f"User {user_id} not found")

        if not user.is_profiled:
            raise Exception("User belum mengisi profil cold start")

        # Profil permanen (dari cold start)
        features = {
            'plan_type': user.plan_type,
            'device_brand': user.device_brand,
            'pct_video_usage': user.pct_video_usage,
            'avg_call_duration': user.avg_call_duration,
            'travel_score': user.travel_score
        }

        # Behavioral real-time
        behavioral = FeatureService.calculate_behavioral_features(user_id)
        features.update(behavioral)

        # Update timestamp
        user.last_features_updated = datetime.now()
        db.session.commit()

        return features
```

### 2. Recommendation Service

```python
# services/recommendation_service.py
import pickle
import pandas as pd
import numpy as np
from services.feature_service import FeatureService
from models import User
from database import db

class RecommendationService:

    def __init__(self):
        # Load model artifacts
        self.model = pickle.load(open('models/rf_model.pkl', 'rb'))
        self.scaler = pickle.load(open('models/scaler.pkl', 'rb'))
        self.label_encoder = pickle.load(open('models/label_encoder.pkl', 'rb'))

    def get_recommendation(self, user_id):
        """
        Generate rekomendasi untuk user
        """
        # 1. Ambil features lengkap
        features = FeatureService.get_complete_features(user_id)

        # 2. Preprocessing
        X = self._preprocess_features(features)

        # 3. Scaling
        X_scaled = self.scaler.transform(X)

        # 4. Prediksi
        prediction = self.model.predict(X_scaled)[0]
        proba = self.model.predict_proba(X_scaled)[0]

        # 5. Decode hasil
        offer = self.label_encoder.inverse_transform([prediction])[0]
        confidence = round(max(proba) * 100, 2)

        # 6. Update cache di database
        user = User.query.get(user_id)
        user.last_recommendation = offer
        user.last_recommendation_at = datetime.now()
        user.last_recommendation_confidence = confidence
        db.session.commit()

        return {
            'offer': offer,
            'confidence': confidence,
            'features_used': features
        }

    def _preprocess_features(self, features):
        """
        Convert dict features ke DataFrame dengan one-hot encoding
        """
        # Convert ke DataFrame
        df = pd.DataFrame([features])

        # One-hot encoding untuk categorical
        df_encoded = pd.get_dummies(df, columns=['plan_type', 'device_brand'])

        # Pastikan semua kolom ada (sesuai training)
        expected_columns = self.model.feature_names_in_
        for col in expected_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0

        # Urutkan kolom sesuai training
        return df_encoded[expected_columns]
```

### 3. Routes/Controllers

```python
# routes/main.py
from flask import Blueprint, session, redirect, render_template, request, jsonify
from services.recommendation_service import RecommendationService
from services.feature_service import FeatureService
from models import User
from database import db
from datetime import datetime

main = Blueprint('main', __name__)
recommendation_service = RecommendationService()

# Mapping untuk cold start
VIDEO_MAPPING = {
    'never': 0.0,
    'rarely': 0.15,
    'sometimes': 0.35,
    'often': 0.60,
    'always': 0.85
}

CALL_MAPPING = {
    'no': 0.0,
    'light': 3.5,
    'moderate': 8.0,
    'heavy': 15.0
}

TRAVEL_MAPPING = {
    'never': 0.0,
    'rarely': 0.2,
    'sometimes': 0.4,
    'often': 0.7
}

@main.route('/dashboard')
def dashboard():
    """
    Dashboard utama - Generate rekomendasi fresh setiap kali dibuka
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    user = User.query.get(user_id)

    # Cek apakah sudah profiled
    if not user.is_profiled:
        return redirect('/coldstart-profile')

    # Generate rekomendasi real-time
    try:
        recommendation = recommendation_service.get_recommendation(user_id)

        return render_template('dashboard.html',
            user=user,
            recommended_offer=recommendation['offer'],
            confidence=recommendation['confidence'],
            features=recommendation['features_used']
        )
    except Exception as e:
        return render_template('error.html', error=str(e)), 500


@main.route('/coldstart-profile', methods=['GET', 'POST'])
def coldstart_profile():
    """
    Form cold start - HANYA DIISI SEKALI saat user baru
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    user = User.query.get(user_id)

    # Jika sudah profiled, redirect ke dashboard
    if user.is_profiled:
        return redirect('/dashboard')

    if request.method == 'POST':
        # Simpan jawaban ke database (PERMANENT)
        user.plan_type = request.form['plan_type']
        user.device_brand = request.form['device_brand']
        user.pct_video_usage = VIDEO_MAPPING[request.form['video_habit']]
        user.avg_call_duration = CALL_MAPPING[request.form['call_need']]
        user.travel_score = TRAVEL_MAPPING[request.form['travel_habit']]

        # Set behavioral features default
        user.avg_data_usage_gb = 0
        user.monthly_spend = 0
        user.topup_freq = 0
        user.complaint_count = 0

        # Mark as profiled
        user.is_profiled = True
        user.profiled_at = datetime.now()

        db.session.commit()

        return redirect('/dashboard')

    return render_template('coldstart_form.html')


@main.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """
    User bisa update profil cold start jika mau
    """
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if request.method == 'POST':
        # Update profil permanen
        if request.form.get('plan_type'):
            user.plan_type = request.form['plan_type']

        if request.form.get('device_brand'):
            user.device_brand = request.form['device_brand']

        if request.form.get('video_habit'):
            user.pct_video_usage = VIDEO_MAPPING[request.form['video_habit']]

        if request.form.get('call_need'):
            user.avg_call_duration = CALL_MAPPING[request.form['call_need']]

        if request.form.get('travel_habit'):
            user.travel_score = TRAVEL_MAPPING[request.form['travel_habit']]

        db.session.commit()

        return redirect('/dashboard')

    return render_template('edit_profile.html', user=user)


@main.route('/api/recommendation/refresh', methods=['GET'])
def refresh_recommendation():
    """
    API untuk refresh rekomendasi tanpa reload page
    """
    user_id = session.get('user_id')

    try:
        recommendation = recommendation_service.get_recommendation(user_id)
        return jsonify({
            'status': 'success',
            'data': recommendation
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

---

## 🔄 Update Strategy

### Kapan Features Di-update?

| Trigger Event                 | Features yang Update                               | Cara Update                 |
| ----------------------------- | -------------------------------------------------- | --------------------------- |
| **User login/buka dashboard** | Semua behavioral features                          | Query database real-time    |
| **User checkout paket**       | `avg_data_usage_gb`, `monthly_spend`, `topup_freq` | Auto saat transaksi selesai |
| **User buat complaint**       | `complaint_count`                                  | Auto saat complaint dibuat  |
| **User edit profile**         | Profil permanen                                    | Manual update user          |

### Timeline Update

```
DAY 1 (User Baru):
├─ Cold start form → Profil permanen tersimpan
├─ Behavioral = 0 (belum ada transaksi)
└─ Rekomendasi = Berdasarkan profil + behavioral default

DAY 3 (Beli paket 1x):
├─ avg_data_usage_gb = 3 GB
├─ monthly_spend = 50,000
├─ topup_freq = 1
└─ Rekomendasi = Update otomatis saat buka dashboard

DAY 15 (Beli paket 3x):
├─ avg_data_usage_gb = (3 + 5 + 3) / 3 = 3.67 GB
├─ monthly_spend = 150,000
├─ topup_freq = 3
└─ Rekomendasi = Makin akurat!

DAY 30 (User Aktif + 1x Komplain):
├─ avg_data_usage_gb = hitung dari semua transaksi
├─ monthly_spend = total 30 hari
├─ topup_freq = total transaksi
├─ complaint_count = 1
└─ Rekomendasi = Sangat personal!

DAY 31 (Rolling Window):
├─ Transaksi hari ke-1 tidak dihitung (>30 hari)
└─ Always fresh data (30 hari terakhir)
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REGISTRATION                         │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              COLD START FORM (5 Pertanyaan)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. plan_type         → users.plan_type               │   │
│  │ 2. device_brand      → users.device_brand            │   │
│  │ 3. video_habit       → users.pct_video_usage         │   │
│  │ 4. call_need         → users.avg_call_duration       │   │
│  │ 5. travel_habit      → users.travel_score            │   │
│  └──────────────────────────────────────────────────────┘   │
│  is_profiled = TRUE                                          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  FIRST RECOMMENDATION                        │
│  (Profil + Behavioral default = 0)                          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    USER ACTIVITIES                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ • Checkout paket  → transactions table               │   │
│  │ • Buat complaint  → complaints table                 │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│           EVERY LOGIN/DASHBOARD ACCESS                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Query transactions (30 hari)                      │   │
│  │ 2. Query complaints (30 hari)                        │   │
│  │ 3. Hitung behavioral features                        │   │
│  │ 4. Gabung dengan profil permanen                     │   │
│  │ 5. Preprocessing & Encoding                          │   │
│  │ 6. Model.predict()                                   │   │
│  │ 7. Update cache rekomendasi                          │   │
│  │ 8. Tampilkan ke user                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Implementasi

### Phase 1: Database Setup

- [ ] Create tabel `users` dengan semua kolom
- [ ] Create tabel `transactions`
- [ ] Create tabel `complaints`
- [ ] Create tabel `packages` (optional)
- [ ] Setup indexes untuk performa query
- [ ] Test insert/query data

### Phase 2: Model Training

- [ ] Preprocessing data (exclude `sms_freq`)
- [ ] Train model dengan 8 fitur + encoding
- [ ] Save model artifacts (model, scaler, label_encoder)
- [ ] Test model prediction

### Phase 3: Backend Services

- [ ] Implement `FeatureService`
- [ ] Implement `RecommendationService`
- [ ] Test feature calculation
- [ ] Test recommendation generation

### Phase 4: Routes/API

- [ ] Route `/coldstart-profile` (GET, POST)
- [ ] Route `/dashboard`
- [ ] Route `/profile/edit`
- [ ] API `/api/recommendation/refresh`
- [ ] Middleware authentication

### Phase 5: Frontend

- [ ] Form cold start dengan 5 pertanyaan
- [ ] Dashboard dengan rekomendasi
- [ ] Halaman edit profile
- [ ] Loading states & error handling

### Phase 6: Testing

- [ ] Unit test services
- [ ] Integration test API
- [ ] End-to-end test flow
- [ ] Load testing
- [ ] User acceptance testing

### Phase 7: Deployment

- [ ] Setup production database
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Setup monitoring & logging
- [ ] Setup backup strategy

---

## 📝 Catatan Penting

### Keputusan Desain

1. **Mengapa 30 hari?**

   - Balance antara data yang cukup vs relevansi
   - Terlalu panjang → data lama tidak relevan
   - Terlalu pendek → data tidak cukup

2. **Mengapa profil permanen?**

   - Kebiasaan user relatif stabil
   - Mengurangi friction (tidak tanya terus)
   - User bisa update manual jika berubah

3. **Mengapa real-time calculation?**
   - Data selalu fresh
   - Tidak perlu background job kompleks
   - Query cepat dengan index yang tepat

### Optimisasi Performa

1. **Database Indexes**

   ```sql
   CREATE INDEX idx_user_date ON transactions(user_id, transaction_date);
   CREATE INDEX idx_complaint_user_date ON complaints(user_id, created_at);
   ```

2. **Caching (Optional)**

   ```python
   # Cache rekomendasi 1 jam
   if cache_age < 3600:
       return cached_recommendation
   ```

3. **Query Optimization**
   ```python
   # Gunakan specific columns, bukan SELECT *
   transactions = Transaction.query\
       .with_entities(Transaction.package_gb, Transaction.amount)\
       .filter(...)\
       .all()
   ```

---

## 📚 Referensi

- Model: Random Forest Classifier
- Framework: Flask/FastAPI
- Database: MySQL/PostgreSQL
- Preprocessing: scikit-learn
- Encoding: One-hot encoding untuk categorical

---

**Dokumentasi dibuat:** 18 November 2025  
**Versi:** 1.0  
**Author:** Telco Recommendation System Team
