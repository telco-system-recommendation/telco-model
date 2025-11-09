# Pertanyaan Cold Start - Sistem Rekomendasi Telco

## Tujuan

Mengumpulkan informasi dasar tentang behavior user untuk memberikan rekomendasi produk/paket yang sesuai di awal penggunaan sistem (cold start problem).

---

## 🎯 Pertanyaan Cold Start (8-10 Pertanyaan)

### 1. **apa minat Tipe Paket Anda Saat Ini?**

_Untuk memahami preferensi dasar pelanggan_

- [ ] Prabayar (Prepaid)
- [ ] Pascabayar (Postpaid)
- [ ] Belum punya paket

---

### 2. **berapa Rata-rata Penggunaan Internet anda Per Bulan?**

_Indikator kebutuhan kuota utama_

- [ ] Ringan (<5 GB) - Browsing & chat ringan
- [ ] Sedang (5-20 GB) - Social media & video kadang-kadang
- [ ] Berat (20-50 GB) - Streaming & gaming rutin
- [ ] Sangat Berat (>50 GB) - Heavy user, work from home

---

### 3. **apa Aktivitas favorit anda?** _(Pilih maksimal 3)_

_Memahami pola penggunaan aplikasi_

- [ ] 📱 Social Media (Instagram, Facebook, Twitter, TikTok)
- [ ] 🎥 Streaming Video (YouTube, Netflix, Disney+)
- [ ] 🎮 Gaming Online (Mobile Legends, PUBG, Free Fire)
- [ ] 🎵 Streaming Musik (Spotify, YouTube Music)
- [ ] 💼 Work/Study (Email, Zoom, Google Meet)
- [ ] 🌐 Browsing & Berita
- [ ] 💬 Chatting (WhatsApp, Telegram, Line)
- [ ] 📤 Cloud Storage & Upload

---

### 4. **Seberapa Sering Anda Menonton Video Streaming?**

_Video usage adalah penggunaan data terbesar_

- [ ] Tidak pernah
- [ ] Jarang (1-2 kali seminggu)
- [ ] Sering (3-5 kali seminggu)
- [ ] Setiap hari
- [ ] Sangat sering (beberapa jam per hari)

---

### 5. **Brand Smartphone/Device Utama Anda**

_Device brand dapat mengindikasikan segmen & preferensi_

- [ ] Samsung
- [ ] Xiaomi
- [ ] Oppo
- [ ] Vivo
- [ ] Realme
- [ ] Apple (iPhone)
- [ ] Lainnya

---

### 6. **Berapa Rata-rata Pengeluaran Pulsa/Paket anda Per Bulan?**

_Price sensitivity & budget range_

- [ ] < Rp 50.000
- [ ] Rp 50.000 - Rp 100.000
- [ ] Rp 100.000 - Rp 200.000
- [ ] > Rp 200.000

---

### 7. **Seberapa Sering Anda Melakukan Top-up/Isi Ulang?**

_Indikator pola konsumsi dan loyalty_

- [ ] Jarang (1-2 kali per bulan)
- [ ] Kadang-kadang (3-4 kali per bulan)
- [ ] Sering (5-7 kali per bulan)
- [ ] Sangat sering (>7 kali per bulan)

---

### 8. **Fitur Apa yang Paling Penting Bagi Anda?** _(Pilih maksimal 2)_

_Understanding priority & preference_

- [ ] 💰 Harga murah
- [ ] 📊 Kuota besar
- [ ] ⚡ Kecepatan tinggi
- [ ] 🎁 Bonus aplikasi (unlimited social media, streaming)
- [ ] 📞 Gratis nelpon/SMS
- [ ] 🌍 Roaming murah
- [ ] ♻️ Rollover kuota (kuota tidak hangus)

---

### 9. **Seberapa Sering Anda Bepergian/Traveling?**

_Travel behavior untuk roaming needs_

- [ ] Tidak pernah
- [ ] Jarang (1-2 kali per tahun)
- [ ] Kadang-kadang (3-5 kali per tahun)
- [ ] Sering (>5 kali per tahun)

---

### 10. **Apakah Anda Tertarik dengan Paket Bundling?**

_Checking interest in bundled offers_

Contoh: Paket data + streaming music/video, paket keluarga, dll.

- [ ] Ya, sangat tertarik
- [ ] Mungkin, tergantung harga
- [ ] Tidak tertarik
- [ ] Tidak tahu

---

## 📊 Mapping ke Fitur Model

Pertanyaan di atas akan di-mapping ke fitur-fitur berikut untuk model ML:

| Pertanyaan       | Fitur Model         | Tipe Data                      |
| ---------------- | ------------------- | ------------------------------ |
| Pertanyaan 1     | `plan_type`         | Categorical (Prepaid/Postpaid) |
| Pertanyaan 2     | `avg_data_usage_gb` | Numerical                      |
| Pertanyaan 3 & 4 | `pct_video_usage`   | Numerical (0-1)                |
| Pertanyaan 5     | `device_brand`      | Categorical                    |
| Pertanyaan 6     | `monthly_spend`     | Numerical                      |
| Pertanyaan 7     | `topup_freq`        | Numerical                      |
| Pertanyaan 9     | `travel_score`      | Numerical (0-1)                |

---

## 🎨 Rekomendasi UI/UX

### Format Presentasi:

1. **Progress Bar**: Tunjukkan "8 dari 10 pertanyaan"
2. **Estimasi Waktu**: "~2 menit untuk selesai"
3. **Skip Option**: Beri opsi "Lewati" dengan konsekuensi rekomendasi umum
4. **Visual Icons**: Gunakan emoji/icon untuk setiap pertanyaan
5. **Swipe/Navigation**: Satu pertanyaan per halaman (mobile-friendly)

### Prioritas Bertanya:

- **Must Have (P0)**: Pertanyaan 1, 2, 3, 6
- **Should Have (P1)**: Pertanyaan 4, 5, 7
- **Nice to Have (P2)**: Pertanyaan 8, 9, 10

---

## 💡 Tips Implementasi

1. **Adaptive Questioning**: Jika user pilih "Tidak pernah streaming", skip detail pertanyaan video
2. **Default Values**: Untuk pertanyaan yang di-skip, gunakan median/mode dari data historis
3. **Progressive Disclosure**: Mulai dengan 5 pertanyaan paling penting, offer "lengkapi profil" nanti
4. **Validation**: Pastikan input masuk akal (misal: high data usage tapi jarang streaming = questionable)

---

## 🔄 Update Behavior Over Time

Setelah cold start, sistem dapat:

- Track actual usage vs declared behavior
- Update profile secara implicit berdasarkan transaksi
- Periodic re-ask (setiap 3-6 bulan) untuk update preferensi
- A/B test pertanyaan mana yang paling predictive

---

**Last Updated**: November 8, 2025
**Version**: 1.0 - Cold Start Simplified
