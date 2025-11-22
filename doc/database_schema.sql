-- ============================================================================
-- TELCO RECOMMENDATION SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Version: 1.0
-- Created: 2025-11-18
-- Description: Complete database schema untuk sistem rekomendasi telco
--              dengan cold start dan behavioral tracking
-- ============================================================================

-- Drop tables jika sudah ada (untuk development)
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS packages;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- TABLE: users
-- Description: Menyimpan data autentikasi dan identitas user
--              HANYA untuk login, registrasi, dan manajemen akun
-- ============================================================================
CREATE TABLE users (
    -- ========== IDENTITY ==========
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    full_name VARCHAR(255),
    
    -- ========== AUTHENTICATION ==========
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed password (bcrypt/argon2)',
    
    -- ========== STATUS & SECURITY ==========
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Status aktif user',
    is_verified BOOLEAN DEFAULT FALSE COMMENT 'Email/phone sudah diverifikasi',
    email_verified_at TIMESTAMP COMMENT 'Timestamp verifikasi email',
    
    -- ========== AUDIT ==========
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP COMMENT 'Login terakhir',
    
    -- ========== INDEXES ==========
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel autentikasi dan identitas user';


-- ============================================================================
-- TABLE: user_profiles
-- Description: Menyimpan profil cold start (permanen) dan
--              behavioral features (dihitung real-time)
--              TERPISAH dari tabel users untuk performa & security
-- ============================================================================
CREATE TABLE user_profiles (
    -- ========== IDENTITY ==========
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    
    -- ========== PROFIL PERMANEN (Cold Start) ==========
    -- Diisi sekali saat user baru, jarang berubah
    -- Bisa diupdate manual melalui "Edit Profile"
    
    plan_type VARCHAR(20) COMMENT 'Prepaid atau Postpaid',
    device_brand VARCHAR(50) COMMENT 'Samsung, Xiaomi, Apple, Oppo, Vivo, Realme, Huawei',
    pct_video_usage FLOAT DEFAULT 0 COMMENT 'Persentase penggunaan video (0.0 - 1.0)',
    avg_call_duration FLOAT DEFAULT 0 COMMENT 'Rata-rata durasi panggilan dalam menit',
    travel_score FLOAT DEFAULT 0 COMMENT 'Skor kebiasaan traveling (0.0 - 1.0)',
    
    -- Metadata Cold Start
    is_profiled BOOLEAN DEFAULT FALSE COMMENT 'Flag apakah user sudah mengisi cold start form',
    profiled_at TIMESTAMP COMMENT 'Timestamp kapan user mengisi profil',
    
    -- ========== BEHAVIORAL FEATURES (Real-time) ==========
    -- Dihitung otomatis dari transactions dan complaints
    -- Update setiap user login/buka dashboard
    
    avg_data_usage_gb FLOAT DEFAULT 0 COMMENT 'Rata-rata GB per transaksi (30 hari terakhir)',
    monthly_spend FLOAT DEFAULT 0 COMMENT 'Total pengeluaran 30 hari terakhir',
    topup_freq INT DEFAULT 0 COMMENT 'Jumlah top-up/checkout 30 hari terakhir',
    complaint_count INT DEFAULT 0 COMMENT 'Jumlah komplain 30 hari terakhir',
    
    -- Metadata Behavioral
    last_features_updated TIMESTAMP COMMENT 'Timestamp terakhir behavioral features dihitung',
    
    -- ========== CACHE REKOMENDASI ==========
    -- Menyimpan hasil rekomendasi terakhir untuk performa
    
    last_recommendation VARCHAR(100) COMMENT 'Hasil rekomendasi terakhir (General Offer, Streaming Offer, dll)',
    last_recommendation_at TIMESTAMP COMMENT 'Timestamp rekomendasi terakhir dibuat',
    last_recommendation_confidence FLOAT COMMENT 'Confidence score rekomendasi (0-100)',
    
    -- ========== AUDIT ==========
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- ========== FOREIGN KEYS ==========
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- ========== INDEXES ==========
    INDEX idx_user_id (user_id),
    INDEX idx_is_profiled (is_profiled),
    INDEX idx_last_recommendation_at (last_recommendation_at),
    
    -- ========== CONSTRAINTS ==========
    CONSTRAINT chk_plan_type CHECK (plan_type IN ('Prepaid', 'Postpaid')),
    CONSTRAINT chk_pct_video_usage CHECK (pct_video_usage BETWEEN 0 AND 1),
    CONSTRAINT chk_travel_score CHECK (travel_score BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel profil user, cold start, dan behavioral features';


-- ============================================================================
-- TABLE: transactions
-- Description: Menyimpan semua transaksi pembelian paket
--              Digunakan untuk menghitung behavioral features:
--              - avg_data_usage_gb, monthly_spend, topup_freq
-- ============================================================================
CREATE TABLE transactions (
    -- ========== IDENTITY ==========
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    
    -- ========== DETAIL PAKET ==========
    package_id INT COMMENT 'Reference ke tabel packages (optional)',
    package_name VARCHAR(255) NOT NULL COMMENT 'Nama paket yang dibeli',
    package_gb FLOAT NOT NULL COMMENT 'Jumlah GB dalam paket (untuk hitung avg_data_usage_gb)',
    package_validity_days INT COMMENT 'Masa aktif paket dalam hari',
    
    -- ========== BILLING ==========
    amount FLOAT NOT NULL COMMENT 'Harga paket (untuk hitung monthly_spend)',
    payment_method VARCHAR(50) COMMENT 'Metode pembayaran: credit_card, ewallet, transfer, dll',
    
    -- ========== STATUS ==========
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'Status transaksi',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Tanggal transaksi dibuat',
    completed_at TIMESTAMP COMMENT 'Tanggal transaksi selesai/berhasil',
    
    -- ========== AUDIT ==========
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- ========== FOREIGN KEYS ==========
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- ========== INDEXES ==========
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_user_date (user_id, transaction_date) COMMENT 'Composite index untuk query behavioral features',
    INDEX idx_completed_at (completed_at),
    
    -- ========== CONSTRAINTS ==========
    CONSTRAINT chk_status CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    CONSTRAINT chk_amount CHECK (amount >= 0),
    CONSTRAINT chk_package_gb CHECK (package_gb >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel transaksi pembelian paket';


-- ============================================================================
-- TABLE: complaints
-- Description: Menyimpan komplain/keluhan user
--              Digunakan untuk menghitung complaint_count
-- ============================================================================
CREATE TABLE complaints (
    -- ========== IDENTITY ==========
    complaint_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    
    -- ========== DETAIL KOMPLAIN ==========
    subject VARCHAR(255) NOT NULL COMMENT 'Judul komplain',
    description TEXT COMMENT 'Deskripsi lengkap komplain',
    category VARCHAR(50) COMMENT 'Kategori: network, billing, service, technical, other',
    priority VARCHAR(20) DEFAULT 'normal' COMMENT 'Prioritas komplain',
    
    -- ========== STATUS ==========
    status VARCHAR(20) DEFAULT 'open' COMMENT 'Status penanganan komplain',
    resolution TEXT COMMENT 'Solusi/penyelesaian komplain',
    
    -- ========== TIMESTAMPS ==========
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Tanggal komplain dibuat',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP COMMENT 'Tanggal komplain diselesaikan',
    
    -- ========== FOREIGN KEYS ==========
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- ========== INDEXES ==========
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_user_date (user_id, created_at) COMMENT 'Composite index untuk query complaint_count',
    INDEX idx_category (category),
    
    -- ========== CONSTRAINTS ==========
    CONSTRAINT chk_complaint_status CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel komplain/keluhan user';


-- ============================================================================
-- TABLE: packages (OPTIONAL)
-- Description: Master data paket-paket yang tersedia
--              Opsional, bisa digunakan untuk referensi
-- ============================================================================
CREATE TABLE packages (
    -- ========== IDENTITY ==========
    package_id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- ========== DETAIL PAKET ==========
    package_name VARCHAR(255) NOT NULL COMMENT 'Nama paket',
    package_type VARCHAR(50) COMMENT 'Tipe: data, voice, combo, unlimited',
    description TEXT COMMENT 'Deskripsi paket',
    
    -- ========== KUOTA ==========
    data_gb FLOAT COMMENT 'Kuota data dalam GB',
    voice_minutes INT COMMENT 'Kuota telepon dalam menit',
    sms_count INT COMMENT 'Kuota SMS',
    
    -- ========== PRICING ==========
    price FLOAT NOT NULL COMMENT 'Harga paket',
    validity_days INT COMMENT 'Masa aktif dalam hari',
    
    -- ========== STATUS ==========
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Status paket masih dijual atau tidak',
    
    -- ========== AUDIT ==========
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- ========== INDEXES ==========
    INDEX idx_package_type (package_type),
    INDEX idx_is_active (is_active),
    INDEX idx_price (price),
    
    -- ========== CONSTRAINTS ==========
    CONSTRAINT chk_package_price CHECK (price >= 0),
    CONSTRAINT chk_data_gb CHECK (data_gb >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Master data paket telco';


-- ============================================================================
-- SAMPLE DATA (untuk testing)
-- ============================================================================

-- Insert sample user
INSERT INTO users (email, phone, full_name, password_hash, is_active, is_verified)
VALUES (
    'user@example.com',
    '081234567890',
    'John Doe',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeOvHp0XoVDq',  -- hashed "password123"
    TRUE,
    TRUE
);

-- Insert user profile (cold start sudah diisi)
INSERT INTO user_profiles (
    user_id,
    plan_type, device_brand, pct_video_usage, avg_call_duration, travel_score,
    is_profiled, profiled_at,
    avg_data_usage_gb, monthly_spend, topup_freq, complaint_count
) VALUES (
    1,  -- user_id dari tabel users
    'Prepaid',
    'Samsung',
    0.60,   -- Sering nonton video
    8.0,    -- Moderate call duration
    0.4,    -- Kadang traveling
    TRUE,
    NOW(),
    3.5,    -- Rata-rata 3.5 GB per transaksi
    125000, -- Total spend 125k
    3,      -- 3 kali top-up
    0       -- Tidak ada komplain
);

-- Insert sample transactions
INSERT INTO transactions (user_id, package_name, package_gb, amount, status, transaction_date, completed_at)
VALUES 
    (1, 'Paket Internet 3GB', 3.0, 35000, 'completed', DATE_SUB(NOW(), INTERVAL 25 DAY), DATE_SUB(NOW(), INTERVAL 25 DAY)),
    (1, 'Paket Internet 5GB', 5.0, 50000, 'completed', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 15 DAY)),
    (1, 'Paket Internet 3GB', 3.0, 35000, 'completed', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY));

-- Insert sample complaint
INSERT INTO complaints (user_id, subject, description, category, status, created_at)
VALUES 
    (1, 'Jaringan lambat', 'Koneksi internet sangat lambat di area rumah', 'network', 'resolved', DATE_SUB(NOW(), INTERVAL 20 DAY));


-- ============================================================================
-- USEFUL QUERIES
-- ============================================================================

-- Query untuk menghitung behavioral features (seperti di FeatureService)
-- Ganti @user_id dan @thirty_days_ago sesuai kebutuhan

-- 1. Hitung avg_data_usage_gb, monthly_spend, topup_freq
SELECT 
    user_id,
    COUNT(*) as topup_freq,
    ROUND(AVG(package_gb), 2) as avg_data_usage_gb,
    ROUND(SUM(amount), 2) as monthly_spend
FROM transactions
WHERE 
    user_id = @user_id
    AND transaction_date >= @thirty_days_ago
    AND status = 'completed'
GROUP BY user_id;

-- 2. Hitung complaint_count
SELECT 
    user_id,
    COUNT(*) as complaint_count
FROM complaints
WHERE 
    user_id = @user_id
    AND created_at >= @thirty_days_ago
GROUP BY user_id;

-- 3. Get complete user features (JOIN users + user_profiles)
SELECT 
    u.user_id,
    u.email,
    u.full_name,
    p.plan_type,
    p.device_brand,
    p.pct_video_usage,
    p.avg_call_duration,
    p.travel_score,
    p.avg_data_usage_gb,
    p.monthly_spend,
    p.topup_freq,
    p.complaint_count,
    p.last_recommendation,
    p.last_recommendation_at,
    p.is_profiled
FROM users u
LEFT JOIN user_profiles p ON u.user_id = p.user_id
WHERE u.user_id = @user_id;


-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- Archive old transactions (older than 1 year)
-- CREATE TABLE transactions_archive LIKE transactions;
-- INSERT INTO transactions_archive SELECT * FROM transactions WHERE transaction_date < DATE_SUB(NOW(), INTERVAL 1 YEAR);
-- DELETE FROM transactions WHERE transaction_date < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- Cleanup incomplete transactions (pending > 24 hours)
-- UPDATE transactions 
-- SET status = 'cancelled' 
-- WHERE status = 'pending' 
-- AND transaction_date < DATE_SUB(NOW(), INTERVAL 24 HOUR);


-- ============================================================================
-- PERFORMANCE MONITORING
-- ============================================================================

-- Check index usage
-- SHOW INDEX FROM users;
-- SHOW INDEX FROM transactions;
-- SHOW INDEX FROM complaints;

-- Analyze query performance
-- EXPLAIN SELECT ... FROM transactions WHERE ...;
