Here is the documentation for the main.ipynb notebook and the experimental results.

# Telco Customer Offer Prediction - Experiment Documentation

## 1. Notebook Overview: main.ipynb

This notebook serves as the core experimental pipeline for predicting customer target offers. It covers the end-to-end machine learning workflow from data loading to model evaluation.

### **Workflow Stages**

1.  **Data Loading & Preprocessing**
    *   Loads raw data from `../data/raw/data_capstone.csv`.
    *   **Outlier Handling:** Detects and removes outliers using the IQR method.
    *   **Data Cleaning:** Removes rows with negative numeric values.
    *   **Feature Selection:** Drops low-importance features (`sms_freq`, `avg_call_duration`) based on prior EDA.
    *   **Encoding:**
        *   Target Variable: Label Encoding.
        *   Categorical Features: One-Hot Encoding.
    *   **Scaling:** Standard Scaling applied to features.

2.  **Data Splitting & Balancing**
    *   **Split:** 80/20 Train-Test split with stratification.
    *   **Balancing:** Applies **SMOTE** (Synthetic Minority Over-sampling Technique) to the training set to handle the severe class imbalance (89:1 ratio).
    *   **Artifact Saving:** Saves processed arrays (`.npy`), scalers, and encoders (`.pkl`) to `../data/processed/`.

3.  **Modeling**
    The notebook trains and evaluates the following models:
    *   **XGBoost:** Trained on *original (unbalanced)* data (CPU).
    *   **LightGBM:** Trained on *balanced* data (supports MPS/GPU).
    *   **Random Forest:** Trained on *balanced* data with `class_weight='balanced'`.
    *   **Gradient Boosting:** Trained on *balanced* data with sample weights.
    *   **CatBoost:** Trained on *balanced* data (CPU).
    *   **CatBoost (Original):** Trained on *original* data (CPU).

4.  **Evaluation Metrics**
    *   F1-Score (Weighted & Macro)
    *   ROC-AUC (One-vs-Rest)
    *   Confusion Matrix
    *   Classification Report

## 2. Experimental Results

The results are aggregated in `../data/result/model_comparison_with_outlierRemoval_fix.csv`.

### **Performance Summary**

The models are ranked by **Macro F1 Score** to prioritize balanced performance across all classes (especially the minority class).

| Rank | Model | Data Strategy | Macro F1 | F1 Weighted | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **CatBoost** | Balanced (SMOTE) | **0.9968** | **0.9978** | **1.0000** |
| **2** | **CatBoost** | Original (Imbalanced) | 0.9855 | 0.9972 | 1.0000 |
| **3** | **LightGBM** | Balanced (SMOTE) | 0.9833 | 0.9972 | 0.9999 |
| **4** | **XGBoost** | Original (Imbalanced) | 0.9715 | 0.9983 | 1.0000 |
| **5** | **Gradient Boosting** | Balanced (SMOTE) | 0.9555 | 0.9949 | 0.9999 |
| **6** | **Random Forest** | Balanced (SMOTE) | 0.7229 | 0.7820 | 0.9904 |

*> **Note:** The values above are taken directly from `../data/result/model_comparison_with_outlierRemoval_fix.csv`.*

### **Key Findings**

1.  **Winner (CatBoost + SMOTE):** Achieved the highest Macro F1 (0.9968), indicating near-perfect classification across all classes, including the minority "Voice Bundle".
2.  **CatBoost Dominance:** Both balanced and original CatBoost models performed exceptionally well, securing the top 2 spots.
3.  **XGBoost Performance:** While XGBoost on original data had the highest Weighted F1 (0.9983), its lower Macro F1 (0.9715) compared to CatBoost suggests slightly less effectiveness on minority classes.
4.  **Random Forest Lag:** Random Forest significantly underperformed compared to boosting methods, highlighting the superiority of gradient boosting for this dataset.

### **Saved Artifacts**

*   **Processed Data:** processed (Train/Test arrays).
*   **Models/Scalers:** `scaler.pkl`, `label_encoder.pkl`, `feature_names.pkl`.
*   **Plots:** smote_comparison.png (Visualizes the class distribution shift).
*   **Results CSV:** model_comparison_with_outlierRemoval_fix.csv.