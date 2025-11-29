# Modular ML Retraining System

## Architecture Overview

This directory implements a **loosely-coupled, modular architecture** for ML model serving and automated retraining, following clean architecture principles and separation of concerns.

### Design Principles

✅ **Separation of Concerns**: Each module has a single, well-defined responsibility  
✅ **Loose Coupling**: Modules interact through clean interfaces  
✅ **Testability**: Each component can be tested independently  
✅ **Maintainability**: Easy to modify, extend, or replace individual components  
✅ **Scalability**: Easy to add new features without breaking existing code

---

## Directory Structure

```
src/
├── app.py                          # FastAPI entrypoint (routes only)
├── retrain_example.py              # Example usage scripts
├── retrain.py                      # Legacy retrain (deprecated)
|                        # Application package (NEW MODULAR STRUCTURE)
├── __init__.py
│
├── schemas/                    # Shared data structures (Pydantic)
│   ├── __init__.py
│   └── model_schemas.py        # Request/Response/Data models
│
├── data_ingestion/             # Fetching & counting data
│   ├── __init__.py
│   ├── repository.py           # Data access logic (CSV/SQL/API)
│   └── stats.py                # Prediction counter logic
│
├── preprocessing/              # Data transformation
│   ├── __init__.py
│   └── pipeline.py             # Cleaning, encoding, scaling
│
├── training/                   # Model training
│   ├── __init__.py
│   └── trainer.py              # Training and evaluation logic
│
├── serialization/              # Format conversion
│   ├── __init__.py
│   └── onnx_exporter.py        # .pkl → .onnx conversion
│
├── storage/                    # Persistence & backup
│   ├── __init__.py
│   └── artifact_manager.py     # Save/load/version models
│
└── services/                   # Orchestration (THE GLUE)
    ├── __init__.py
    └── retraining_service.py   # Coordinates all modules
```

---

## Component Responsibilities

### 1. **schemas/** - Data Contracts

📝 **Purpose**: Defines shared data structures using Pydantic

**Key files**:

- `model_schemas.py`: API request/response models, internal data structures

**Classes**:

- `PredictRequest`: API prediction request
- `PredictResponse`: API prediction response
- `TrainingData`: Internal training data format
- `RetrainResult`: Retraining operation result

**Example**:

```python
from app.schemas.model_schemas import PredictRequest, RetrainResult
```

---

### 2. **data_ingestion/** - Data Access Layer

📦 **Purpose**: Handles all data fetching and prediction counting

**Key files**:

- `repository.py`: DataRepository class
- `stats.py`: PredictionCounter class

**Responsibilities**:

- Load original training data (.npy files)
- Manage prediction buffer (CSV)
- Increment/reset prediction counter
- Load preprocessing artifacts (scaler, encoder, features)
- Save training data for next cycle

**Example**:

```python
from app.data_ingestion import DataRepository, PredictionCounter

# Load training data
repo = DataRepository()
X, y = repo.load_original_training_data()

# Manage counter
counter = PredictionCounter()
count = counter.increment()
should_retrain = counter.should_retrain(threshold=1000)
```

---

### 3. **preprocessing/** - Data Transformation

🧹 **Purpose**: All data cleaning and feature engineering

**Key files**:

- `pipeline.py`: PreprocessingPipeline class

**Responsibilities**:

- Outlier removal (IQR method)
- Negative value handling
- Categorical encoding (one-hot)
- Feature scaling (StandardScaler)
- Target label encoding
- Column alignment with training features

**Example**:

```python
from app.preprocessing import PreprocessingPipeline

pipeline = PreprocessingPipeline(scaler, label_encoder, feature_names)

# Preprocess new data
X_scaled, y_encoded = pipeline.preprocess_new_data(df)
```

---

### 4. **training/** - Model Training

🎯 **Purpose**: Model training and evaluation logic

**Key files**:

- `trainer.py`: ModelTrainer class

**Responsibilities**:

- Apply SMOTE for class balancing
- Train CatBoost classifier
- Evaluate model performance
- Generate metrics (F1-Weighted, F1-Macro, ROC-AUC)
- Create classification reports

**Example**:

```python
from app.training import ModelTrainer

trainer = ModelTrainer()
model, metrics = trainer.train_and_evaluate(
    X, y, label_encoder,
    apply_balancing=True,
    test_size=0.2
)

print(f"F1-Weighted: {metrics['f1_weighted']:.4f}")
```

---

### 5. **serialization/** - Format Conversion

🔄 **Purpose**: Converts models between formats

**Key files**:

- `onnx_exporter.py`: ONNXExporter class

**Responsibilities**:

- Convert .pkl → .onnx
- Validate ONNX models
- Handle feature names in export

**Example**:

```python
from app.serialization import ONNXExporter

exporter = ONNXExporter()
success = exporter.export_to_onnx(model, "model.onnx", feature_names)
is_valid = exporter.validate_onnx("model.onnx")
```

---

### 6. **storage/** - Persistence & Versioning

💾 **Purpose**: Manages model artifacts and backups

**Key files**:

- `artifact_manager.py`: ArtifactManager class

**Responsibilities**:

- Save models to disk (joblib)
- Load models from disk
- Create versioned backups
- Cleanup old backups (keep 5 most recent)
- Save training logs
- Track model versions by timestamp

**Example**:

```python
from app.storage import ArtifactManager

manager = ArtifactManager()

# Save model
manager.save_model(model, "best_model.pkl")

# Backup before retrain
backup_path = manager.backup_model("best_model.pkl")

# Cleanup old backups
manager.cleanup_old_backups(keep_latest=5)
```

---

### 7. **services/** - Orchestration Layer (THE GLUE)

🎼 **Purpose**: Coordinates all modules to perform end-to-end workflows

**Key files**:

- `retraining_service.py`: RetrainingService class

**This is the main entry point** - orchestrates all other modules!

**Responsibilities**:

- Log predictions with counter
- Trigger retraining when threshold reached
- Coordinate entire retraining workflow
- Manage complete lifecycle

**Complete Retraining Workflow**:

1. ✅ Backup current model (storage)
2. ✅ Load original training data (data_ingestion)
3. ✅ Load new predictions from buffer (data_ingestion)
4. ✅ Preprocess new data (preprocessing)
5. ✅ Combine old + new data
6. ✅ Train new model with SMOTE (training)
7. ✅ Save model (.pkl) (storage)
8. ✅ Export to ONNX (serialization)
9. ✅ Update training data (data_ingestion)
10. ✅ Log results (storage)
11. ✅ Cleanup and reset (data_ingestion)

**Example**:

```python
from app.services import RetrainingService

# Initialize
service = RetrainingService(retrain_threshold=1000)

# Log predictions (auto-triggers at threshold)
service.log_prediction(features_dict, true_label)

# Get status
status = service.get_status()
print(f"Progress: {status['progress_percent']}%")

# Manual retrain
result = service.retrain()
if result.success:
    print(f"F1-Weighted: {result.f1_weighted:.4f}")
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Run Example Scripts

**Check Status**:

```bash
cd src/
python retrain_example.py status
```

Output:

```
🔍 Checking retraining status...

Current Count: 450
Threshold: 1000
Remaining: 550
Progress: 45.0%
Model Version: 20241127_143022
```

**Test Components**:

```bash
python retrain_example.py test
```

Output:

```
🧪 Testing modular components...

1. Testing DataRepository...
   ✓ Loaded 8500 training samples

2. Testing PredictionCounter...
   ✓ Current count: 450

3. Testing PreprocessingPipeline...
   ✓ Loaded preprocessing artifacts
   - Features: 25
   - Classes: 4

4. Testing ArtifactManager...
   ✓ Found 3 backup(s)

✅ Component tests complete!
```

**Simulate Predictions**:

```bash
python retrain_example.py simulate
```

**Manual Trigger**:

```bash
python retrain_example.py trigger
```

### 3. Start API Server

```bash
uvicorn app:app --reload
```

**API Endpoints**:

- `GET /` - API information
- `POST /predict` - Make predictions
- `GET /health` - Health check
- `GET /retrain/status` - Retraining status

**API Example**:

```python
import requests

response = requests.post("http://localhost:8000/predict", json={
    "inputs": [[0.5, 0.3, 0.7, ...]],  # Scaled features
    "raw_features": [{
        "monthly_spend": 50,
        "avg_data_usage_gb": 2.5,
        "plan_type": "Basic",
        "device_brand": "Samsung",
        ...
    }],
    "true_labels": ["Premium Plan"]
})

print(response.json())
```

---

## Benefits of Modular Architecture

### ✅ 1. Testability

Each module can be unit tested independently:

```python
# Test data repository
def test_repository():
    repo = DataRepository()
    X, y = repo.load_original_training_data()
    assert len(X) > 0
    assert len(X) == len(y)

# Test preprocessing
def test_preprocessing():
    pipeline = PreprocessingPipeline(scaler, encoder, features)
    df = pd.DataFrame({...})
    X, y = pipeline.preprocess_new_data(df)
    assert X.shape[1] == len(features)

# Test trainer
def test_trainer():
    trainer = ModelTrainer()
    model, metrics = trainer.train_and_evaluate(X, y, encoder)
    assert metrics['f1_weighted'] > 0.5
```

### ✅ 2. Maintainability

Change one component without affecting others:

| Change | Module to Modify | Other Modules Affected |
|--------|------------------|------------------------|
| CSV → SQL database | `data_ingestion/repository.py` | None |
| CatBoost → XGBoost | `training/trainer.py` | None |
| Local → S3 storage | `storage/artifact_manager.py` | None |
| Add new feature engineering | `preprocessing/pipeline.py` | None |

### ✅ 3. Extensibility

Easy to add new features:

```python
# Add Redis caching
# app/data_ingestion/cache.py
class RedisCache:
    def get(self, key): ...
    def set(self, key, value): ...

# Add MLflow tracking
# app/storage/mlflow_tracker.py
class MLflowTracker:
    def log_metrics(self, metrics): ...
    def log_model(self, model): ...

# Add data validation
# app/preprocessing/validator.py
class DataValidator:
    def validate_schema(self, df): ...
    def check_drift(self, df): ...
```

### ✅ 4. Loose Coupling

Modules depend on interfaces, not implementations:

- ✅ Service layer doesn't know if data comes from CSV, SQL, or API
- ✅ Trainer doesn't know how models are stored (local disk, S3, etc.)
- ✅ Storage doesn't know what preprocessing was applied
- ✅ Preprocessing doesn't know what model will be trained

### ✅ 5. Clear Separation of Concerns

| Concern | Module |
|---------|--------|
| "Where does data come from?" | `data_ingestion` |
| "How do we clean data?" | `preprocessing` |
| "How do we train models?" | `training` |
| "Where do we save models?" | `storage` |
| "How do we convert formats?" | `serialization` |
| "How does everything work together?" | `services` |

---

## Monitoring & Operations

### Check Retraining Status

```python
from app.services import RetrainingService

service = RetrainingService()
status = service.get_status()

print(f"Current: {status['current_count']}/{status['threshold']}")
print(f"Progress: {status['progress_percent']}%")
print(f"Model Version: {status['model_version']}")
```

### View Logs

```bash
# List all retrain logs
ls -lh ../data/retrain/logs/

# View latest log
cat ../data/retrain/logs/retrain_log_$(ls -t ../data/retrain/logs/ | head -1)
```

### Check Backups

```bash
# List all backups
ls -lh ../data/retrain/backups/

# Count backups
ls ../data/retrain/backups/ | wc -l
```

### Monitor Prediction Buffer

```bash
# Check buffer size
wc -l ../data/retrain/prediction_buffer.csv

# View buffer content
head ../data/retrain/prediction_buffer.csv
```

---

## Troubleshooting

### Issue: Import errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution**: Run from `src/` directory:

```bash
cd src/
python retrain_example.py status
```

### Issue: Preprocessing artifacts not found

```
FileNotFoundError: Training data not found in ../data/processed
```

**Solution**: Run main notebook first to generate artifacts:

```bash
jupyter notebook ../notebook/main.ipynb
```

Required files:

- `data/processed/X_train_original.npy`
- `data/processed/y_train_original.npy`
- `data/processed/scaler.pkl`
- `data/processed/label_encoder.pkl`
- `data/processed/feature_names.pkl`

### Issue: No new data in buffer

```
⚠️ No new data found in buffer. Skipping retrain.
```

**Solution**: Predictions must include raw features and true labels:

```python
# ❌ Wrong - no raw features
response = requests.post("/predict", json={
    "inputs": [[0.5, 0.3, ...]]
})

# ✅ Correct - includes raw features and labels
response = requests.post("/predict", json={
    "inputs": [[0.5, 0.3, ...]],
    "raw_features": [{"monthly_spend": 50, ...}],
    "true_labels": ["Premium Plan"]
})
```

### Issue: No target labels in buffer

```
⚠️ No target labels in buffer. Cannot retrain without ground truth.
```

**Solution**: Always provide `true_labels` when logging predictions:

```python
service.log_prediction(features_dict, true_label="Premium Plan")
```

---

## Future Enhancements

### 1. Database Integration

Replace CSV buffer with database:

```python
# app/data_ingestion/db_repository.py
class DatabaseRepository(DataRepository):
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
    
    def load_prediction_buffer(self):
        return pd.read_sql("SELECT * FROM predictions", self.engine)
```

### 2. MLflow Integration

Track experiments and models:

```python
# app/storage/mlflow_manager.py
class MLflowManager(ArtifactManager):
    def save_model(self, model, model_path):
        super().save_model(model, model_path)
        mlflow.log_model(model, "model")
        mlflow.log_metrics(metrics)
```

### 3. Cloud Storage (S3/GCS)

```python
# app/storage/cloud_manager.py
class S3Manager(ArtifactManager):
    def save_model(self, model, model_path):
        super().save_model(model, model_path)
        s3.upload_file(model_path, bucket, key)
```

### 4. Async Retraining

```python
# app/services/async_retraining_service.py
from celery import Celery

@celery.task
def retrain_async():
    service = RetrainingService()
    result = service.retrain()
    return result
```

### 5. Drift Detection

```python
# app/preprocessing/drift_detector.py
class DriftDetector:
    def detect_feature_drift(self, new_data, reference_data):
        ...
    def detect_target_drift(self, new_predictions, reference):
        ...
```

### 6. A/B Testing

```python
# app/services/ab_testing_service.py
class ABTestingService:
    def compare_models(self, model_a, model_b, test_data):
        ...
    def should_deploy(self, new_model, old_model):
        ...
```

---

## Contributing

When adding new functionality:

1. **Identify the appropriate module** (or create new one)
2. **Implement with clear interface**
3. **Add unit tests**
4. **Update documentation**

**Example: Adding Email Notifications**

```python
# 1. Create new module
# app/notifications/__init__.py
# app/notifications/email_service.py
class EmailService:
    def send_retrain_notification(self, result):
        ...

# 2. Integrate in service layer
# app/services/retraining_service.py
from app.notifications import EmailService

class RetrainingService:
    def __init__(self):
        self.email_service = EmailService()
    
    def retrain(self):
        result = ...
        self.email_service.send_retrain_notification(result)

# 3. Add tests
def test_email_notification():
    service = EmailService()
    result = RetrainResult(...)
    assert service.send_retrain_notification(result) == True

# 4. Update this README!
```

---

## Summary

This modular architecture provides:

- ✅ **Clean separation** of data access, processing, training, and storage
- ✅ **Easy testing** of individual components
- ✅ **Simple maintenance** - change one module without affecting others
- ✅ **Straightforward extension** - add new features with minimal changes
- ✅ **Clear organization** - easy to understand and navigate
- ✅ **Production-ready** - scalable and maintainable

**Main Entry Point**: `app/services/retraining_service.py` (the orchestrator)

**Usage**: Just import `RetrainingService` and you're ready to go!

```python
from app.services import RetrainingService

service = RetrainingService(retrain_threshold=1000)
service.log_prediction(features, label)
```

That's it! The service handles everything else. 🚀
