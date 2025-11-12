# Telco Customer EDA — Executive Summary

## Overview

- Dataset: **10,000** customers, **12** columns (behavioral, spend, plan, device).
- Objective: Understand customer mix, offer targeting, and key drivers of spend to inform product and growth strategy.

## Data insights (utama — siap untuk modeling/recommendation)

- Distribusi pelanggan: **Prepaid 61.08%**, **Postpaid 38.92%** → dominasi Prepaid perlu dipertimbangkan saat membangun model (class imbalance).
- Korelasi paling kuat: `monthly_spend` berkorelasi tinggi dengan `avg_data_usage_gb` (**r ≈ 0.90**) — data usage adalah predictor utama untuk spend/monetization. Fitur lain (`pct_video_usage`, `travel_score`, `sms_freq`, `topup_freq`) menunjukkan korelasi rendah terhadap `monthly_spend`.
- Uji statistik: Mann-Whitney **p ≈ 0.45** → tidak ada perbedaan bermakna pada median `monthly_spend` antara Prepaid vs Postpaid. Chi-square **p ≈ 0.88** → tidak ditemukan asosiasi kuat antara variabel kategori utama yang diuji.
- Segmentasi (KMeans, k=4) — profil cluster ringkas:
   - **Cluster 1 (high-value):** `monthly_spend` ≈ 179k; `complaint_count` moderat; usage tinggi → kandidat utama untuk upsell premium/device upgrade.
   - **Cluster 0:** `monthly_spend` ≈ 94.6k; `travel_score` tinggi → target paket roaming/travel promos.
   - **Cluster 2 & 3:** `monthly_spend` ≈ 91–93k; Cluster 3 menonjol dengan `complaint_count` lebih tinggi → fokus retention / customer service.
   - Perbedaan cluster terutama pada level spend, travel behavior, dan complaint_count — basis segmentasi pragmatis untuk rules/personalization.

## Offer targeting (Top 5)

- General Offer: 6,070 customers (60.7%)
- Device Upgrade Offer: 1,502 (15.02%)
- Data Booster: 797 (7.97%)
- Retention Offer: 761 (7.61%)
- Top-up Promo: 370 (3.70%)

Observation: The portfolio is heavily concentrated on a broad **General Offer**, suggesting room to personalize and diversify offers by need-state.

## Key drivers (model-based feature importance)

Simple Decision Tree (depth=6) with encoded features to gauge signal:

- monthly_spend — 0.274
- complaint_count — 0.177
- device_brand — 0.171
- pct_video_usage — 0.138
- avg_data_usage_gb — 0.131

Interpretation: Spend itself, service issues (complaints), and device context carry meaningful signal, followed by video usage and overall data consumption.

## Spend dynamics (correlations with `monthly_spend`)

- avg_data_usage_gb: +0.90 (strong positive)
- pct_video_usage: +0.01 (near zero)
- travel_score: +0.01 (near zero)
- sms_freq: −0.01 (near zero)
- topup_freq: +0.01 (near zero)

Takeaway: Higher data consumption strongly tracks higher spend; other behaviors show minimal linear correlation.

## Statistical evidence

- Mann–Whitney U (Postpaid vs Prepaid monthly_spend):
  - p-value ≈ 0.453 (not significant at 5%)
  - Median spend: Postpaid ≈ 102,000; Prepaid ≈ 103,000
  - Implication: No statistically significant difference in spend distributions between plan types in this sample.

- Chi-square (device_brand vs plan_type):
  - p-value ≈ 0.878 (not significant)
  - Implication: No evidence of association; device brand doesn’t meaningfully segment plan type.

## Engineered features

- cost_per_gb was created in a cleaned subset (df_cleaned) but not present in the base frame used for summary export; medians by target_offer were not captured.
- Recommendation: Persist `cost_per_gb` to the main dataframe before summarization and re-export medians by target_offer to quantify price-sensitivity segments.

## Product & growth implications

- Personalization opportunity: With 60%+ of customers receiving a General Offer, tailor offers using key drivers (data usage, complaints, device context).
- Monetize heavy data users: Strong usage–spend coupling suggests upsell paths (bigger data bundles, premium video passes) for high-usage cohorts.
- Service-led retention: complaint_count importance implies that resolving service pain points could lift conversion/retention for targeted offers.
- Device-neutral plan strategy: Lack of device–plan association means device brand is not a reliable lever for plan segmentation; focus on behavior instead.

## Recommended next steps

1. Enrich engineered features in pipeline (e.g., cost_per_gb, engagement_score) and save into canonical dataset; re-run summary.
2. Segment by data-usage deciles and complaint tiers; test differentiated offers (data boosters vs. retention bundles).
3. Replace single tree with robust models (e.g., Gradient Boosting/XGBoost) for stable feature attributions; validate with cross-validation.
4. Calibrate business metrics: connect offer acceptance and ARPU uplift per segment to prioritize campaign spend.
5. A/B test 2–3 personalized offer templates against General Offer baseline to quantify lift.


## Business impact — apa artinya bagi produk & revenue

* avg_data_usage_gb sebagai predictor kuat menyederhanakan prioritas engineering: fitur pemakaian data (total + proporsi video) adalah sinyal utama untuk merekomendasikan produk berbayar (Data Booster, higher-tier plans).
* Karena General Offer mendominasi target labels, model rekomendasi perlu mengatasi class imbalance—tanpa itu, model cenderung merekomendasikan General Offer berulang (rendah value uplift).
* Cluster high-value (Cluster 1) adalah sumber ARPU potensial; akuisisi/upsell ke segmen ini memberi return lebih cepat. Sebaliknya, cluster dengan complaint_count tinggi (Cluster 3) memberi peluang retention/CS improvement yang langsung berdampak pada churn reduction.
* Tidak adanya perbedaan signifikan spend antara Prepaid/Postpaid berarti strategi rekomendasi harus personal (behavioral) bukan semata berdasarkan plan_type.

## Recommendations — langkah teknis & bisnis selanjutnya (prioritas)

1. Modeling roadmap (fase 1 → 2):

   * Fase 1: buat model multi-class classification / ranking untuk rekomendasi `target_offer` menggunakan fitur: avg_data_usage_gb, pct_video_usage, topup_freq, travel_score, complaint_count, device_brand, sms_freq. Gunakan stratified sampling dan class weighting / oversampling untuk mengatasi imbalance.
   * Fase 2: upgrade ke Uplift/causal model untuk memilih offer yang meningkatkan conversion/ARPU (bukan sekadar prediksi preferensi).
2. Feature engineering:

   * Hitung features baru: recency/frequency of top-ups, moving averages usage (7/30 hari), cost_per_gb (jika dapat digabungkan dari pricing), engagement signals (video% × avg_data_usage).
   * One-hot encoding untuk device_brand / plan_type atau gunakan embedding untuk model neural/GBM.
3. Segmen & eksperimen:

   * Gunakan cluster hasil KMeans sebagai strata untuk A/B testing: uji offer berbeda di tiap cluster (mis. Device Upgrade vs Data Booster di high-value cluster).
   * Prioritaskan retention play untuk cluster dengan elevated complaint_count (improve CX, special retention offer).
4. Metrics & monitoring:

   * KPI utama: conversion rate per offer, ARPU uplift, retention/churn delta, complaint rate. Lakukan monitoring per-cluster.
5. Operational & product considerations:

   * Hindari rekomendasi yang mengorbankan margin: sertakan constraint bisnis (profitability per offer) dalam model ranking.
   * Pastikan pipeline realtime/near-realtime untuk fitur penggunaan data jika ingin rekomendasi saat user aktif (trigger in-app/push).

## Quick next steps

* Siapkan dataset modeling: buat split train/val/test, engineering features recency/topup patterns, dan atasi class imbalance.
* Bangun baseline model: LightGBM multiclass untuk `target_offer` + evaluation per-cluster (precision@k, recall, conversion proxy).
* Desain 2 A/B tests: (a) High-value cluster — Device Upgrade vs General Offer; (b) Complaint cluster — Retention Offer vs CS-improvement + small promo.
* Metric dashboard: setup ARPU, CTR, conversion rate per-offer & per-cluster.

## Catatan metodologis & keterbatasan

* Data saat ini gak memiliki field `cost_per_gb` (engineered_cost_medians disebut tidak tersedia) — menambahkan pricing/COGS akan membantu optimasi profit-aware recommendations.
* Hasil statistik (Mann-Whitney, chi-square) bergantung pada kolom yang diuji; tidak ditemukan perbedaan signifikan untuk beberapa pertanyaan, namun behaviour features (usage) tetap sangat informatif.
* Visualisasi di notebook (heatmap, cluster centers, distribusi) mendukung temuan — untuk pitch investor, saya sarankan menambahkan 2 slide visual: korelasi monthly_spend vs avg_data_usage_gb + ringkasan profil 4 cluster (bar chart center features).

