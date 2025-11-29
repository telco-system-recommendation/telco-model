# Telco Customer Offer Prediction Repository Overview

## 1. Introduction

This repository (`telco-model`) contains a machine learning project for predicting customer target offers in a telecommunications company. The goal is to analyze customer behavior data and recommend personalized offers (e.g., "General Offer", "Voice Bundle") to improve customer retention and revenue.

The project uses Python-based machine learning libraries to process data, train models, and generate predictions. It's designed to be integrated with frontend (for user interfaces) and backend (for API services) systems.

## 2. Project Purpose and Workflow

### Purpose

- **Predict Customer Offers**: Based on features like monthly spend, data usage, complaint history, and demographics, predict which offer a customer is most likely to accept.
- **Handle Imbalanced Data**: The dataset has a severe class imbalance (89:1 ratio), so models use techniques like SMOTE for balanced training.
- **Provide Deployable Models**: Trained models are saved in formats like `.pkl` and `.onnx` for easy integration into production systems.

### High-Level Workflow

1. **Data Ingestion**: Raw data is loaded from CSV files.
2. **Preprocessing**: Outlier removal, encoding, scaling, and balancing.
3. **Exploratory Data Analysis (EDA)**: Visualize distributions, correlations, and feature importance.
4. **Model Training**: Train and compare multiple models (e.g., CatBoost, XGBoost, Random Forest).
5. **Evaluation**: Assess performance using metrics like F1-score, ROC-AUC.
6. **Deployment**: Save best model for inference in backend systems.

## 3. Folder Structure

Here's a breakdown of the repository structure and the purpose of each folder:

- **`/` (Root)**:
  - `best_model_lgb.joblib`: Serialized LightGBM model (backup or alternative model).
  - `CONTRIBUTING.md`: Guidelines for contributing to the project.
  - `README.md`: General project overview and setup instructions.
  - `requirements.txt`: List of Python dependencies (install with `pip install -r requirements.txt`).

- **`catboost_info/`**:
  - Contains training logs and metadata from CatBoost experiments (e.g., `catboost_training.json`, error logs).
  - Purpose: Debugging and monitoring CatBoost training performance.

- **`data/`**:
  - **`plot/`**: Visualizations from EDA (e.g., correlation heatmaps, feature importance plots).
  - **`processed/`**: Cleaned and transformed data (e.g., `.npy` arrays for training/testing, scalers, encoders).
  - **`raw/`**: Original dataset (e.g., `data_capstone.csv` with customer features).
  - **`result/`**: Model comparison CSVs (e.g., `model_comparison.csv` with F1 scores and rankings).
  - Purpose: Centralized data storage. Raw data is input, processed data is output from notebooks, results are for evaluation.

- **`doc/`**:
  - **`cold_start_recommendation_system.md`**: Documentation on handling new users with no history.
  - **`database_schema.sql`**: SQL schema for storing customer data or predictions.
  - **`documentation/`**: Detailed docs (e.g., `main_notebook.md` for model experiments).
  - **`listPertanyaan_behavior/`**: Behavioral analysis questions and insights.
  - **`researchRequirement/`**: Research notes and requirements.
  - Purpose: Documentation hub for understanding the project, data schema, and research.

- **`model/`**:
  - `best_model.onnx`: Best model in ONNX format for cross-platform inference.
  - Purpose: Deployable model artifacts. Use this for production (e.g., load in backend APIs).

- **`notebook/`**:
  - **`EDA.ipynb`**: Exploratory data analysis (visualizations, correlations).
  - **`explore_testing.ipynb`**: Testing and validation scripts.
  - **`feature_importance_analysis.ipynb`**: Feature selection and importance analysis.
  - **`main.ipynb`**: Core pipeline (preprocessing, training, evaluation, saving).
  - **`model.ipynb`**: Alternative model experiments (messier, experimental).
  - **`preposesingData.ipynb`**: Data cleaning and preparation.
  - Purpose: Jupyter notebooks for development. Run these to reproduce experiments.

- **`src/`**:
  - (Currently empty in the structure, but intended for source code if needed).
  - Purpose: Custom Python modules or scripts (e.g., utility functions).

## 4. Getting Started Guide

### Prerequisites

- Python 3.10+ installed.
- Virtual environment recommended (e.g., `python -m venv .venv`).
- Git for cloning the repository.

### Setup Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/telco-system-recommendation/telco-model.git
   cd telco-model
   ```

2. **Create Virtual Environment**:

   ```bash
   python3.10 -m venv .venv
   ```

3. **Activate Virtual Environment**:

   ```bash
   source .venv/bin/activate  # On macOS/Linux
   ```

4. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
   This installs libraries like pandas, scikit-learn, CatBoost, XGBoost, etc.

5. **Configure Environment Variables**:

   ```bash
   cp .env.example .env
   # edit .env with your secrets (Supabase keys, DB URLs, etc.)
   ```
   The FastAPI service and Docker Compose read every runtime secret from `.env`, so never commit the populated file—`.gitignore` already keeps it private.

6. **Run the Main Notebook**:
   - Open `notebook/main.ipynb` in Jupyter Lab or VS Code.
   - Run cells sequentially to preprocess data, train models, and save results.
   - Key outputs: Processed data in `data/processed/`, results in `data/result/`, best model in `model/best_model.onnx`.

7. **Verify Setup**:
   - Check if `data/raw/data_capstone.csv` exists (this is the input dataset).
   - Run a quick test: Open `notebook/main.ipynb` and execute the first few cells to load data.

### Common Issues

- **Missing Data**: Ensure `data/raw/data_capstone.csv` is present (not included in repo for privacy).
- **GPU Issues**: Models default to CPU; MPS (Mac GPU) may not work for all libraries.
- **Library Conflicts**: Use the virtual environment to avoid conflicts.

## 5. Testing Guide

### How to Test the Models

1. **Unit Testing Data Processing**:
   - Run `notebook/preposesingData.ipynb` to verify data cleaning (e.g., outlier removal, encoding).
   - Check outputs in `data/processed/` (e.g., `X_train.npy` should exist).

2. **Model Training Testing**:
   - Execute `notebook/main.ipynb` end-to-end.
   - Verify model rankings in `data/result/model_comparison.csv` (CatBoost should rank #1).
   - Check saved model: Load `model/best_model.onnx` and make a prediction on sample data.

3. **Performance Validation**:
   - Use the evaluation metrics in the notebook (F1-Weighted, Macro F1, ROC-AUC).
   - Expected: Macro F1 > 0.95 for the best model on test data.

4. **Integration Testing**:
   - Load the ONNX model in a backend script (e.g., using `onnxruntime`).
   - Example code:

     ```python
     import onnxruntime as ort
     import numpy as np

     # Load model
     session = ort.InferenceSession('model/best_model.onnx')

     # Sample input (replace with real features)
     sample_input = np.random.rand(1, 10).astype(np.float32)  # Adjust shape to match features

     # Predict
     outputs = session.run(None, {'input': sample_input})
     print("Prediction:", outputs)
     ```

### Testing Checklist

- [ ] Data loads without errors.
- [ ] Preprocessing completes (no nulls, scaled features).
- [ ] Models train without crashes.
- [ ] Best model saves to ONNX.
- [ ] Predictions match expected format (e.g., offer classes).

## 6. Integration with Frontend and Backend

### For Backend Teams

- **Model Usage**: Load the ONNX model (`model/best_model.onnx`) using `onnxruntime` for fast inference in APIs.
- **Input Format**: Features must be preprocessed (scaled, encoded) like in the notebooks. Use saved scalers (`data/processed/scaler.pkl`).
- **Output**: Model predicts offer classes (e.g., 0 for "General Offer", 1 for "Voice Bundle"). Map to human-readable labels.
- **API Example**: Create an endpoint that takes customer features (JSON) and returns predicted offer.

### For Frontend Teams

- **Understanding Predictions**: The model recommends offers based on user behavior. Display recommendations in the UI (e.g., "Based on your usage, we recommend this offer").
- **Data Flow**: Frontend collects user data (e.g., via forms), sends to backend API, which uses the model to predict and return results.
- **No Direct Access**: Don't modify model files; rely on backend for predictions.

### Key Handover Points

- **Dataset Schema**: Refer to `doc/database_schema.sql` for data structure.
- **Model Specs**: 10+ features (numeric/categorical), multiclass output.
- **Performance**: High accuracy (F1 > 0.99), but test on real data for edge cases.
- **Updates**: If new data arrives, retrain via notebooks and update the ONNX file.

For questions, refer to `README.md` or contact the ML team. This setup ensures the ML pipeline is reproducible and integrable.
