# Release v1.0.0

## Summary

Initial stable production release of the Telco Customer Offer Prediction model (first production-ready release).

## Type of change

- [x] Major (first stable production release => v1.0.0)
- [ ] Minor (backwards-compatible)
- [ ] Patch (bugfix / non-behavioral change)

## Why

This model is production-stable: input/output schema is documented and stable, tests and validation completed, and it is already deployed using the ONNX artifact in production backends.

## Dataset and training

- Dataset source: data/raw/data_capstone.csv (see repository data/)
- Evaluation/results reference: data/result/model_comparison.csv
- Training commit: <REPLACE_WITH_COMMIT_SHA>
- Training config / notebook: notebook/main.ipynb and doc/documentation/main_notebook.md

## Evaluation (repo-sourced)

Primary reported metrics (from data/result/model_comparison.csv and notebook evaluations):

- Best model: CatBoost (Original)
  - F1-Weighted: 0.997443683483641
  - Macro F1: 0.9920642080812804
  - ROC-AUC: 0.9999602853899207

- CatBoost (Balanced / SMOTE)
  - F1-Weighted: 0.9948692457595311
  - Macro F1: 0.983978874793447

> Note: metrics above are extracted from repository evaluation artifacts (data/result/*.csv and notebook outputs). See repo for full comparison table and per-class reports.

## Runtime / Deployment details

- Production artifact: ONNX model (model/best_model.onnx) — recommended runtime: onnxruntime.
- Serving: backend services in this repo are FastAPI-based (src/app.py) and expected to load ONNX via onnxruntime for inference.
- Preprocessing: same preprocessing pipeline as in notebooks must be applied before inference; saved scalers and encoders are under data/processed/ (e.g., scaler.pkl, label_encoder.pkl).
- Hardware: inference is CPU-oriented (training used CPU CatBoost parameters in trainer.py).

## Artifacts included in release

- Model artifact: artifacts/telco-model-v1.0.0.onnx (or model/best_model.onnx)
- Model metadata: artifacts/model_metadata_v1.0.0.json
- Checksum: artifacts/telco-model-v1.0.0.sha256

## Migration notes / Breaking changes

- This is the first stable release (v1.0.0). Consumers can rely on the model input/output schema defined in src/schemas/model_schemas.py.
- Any future change to the schema, label mapping, or output semantics will be a MAJOR version bump.

## Repro instructions

- Training pipeline / notebooks: notebook/main.ipynb
- To reproduce: follow the notebooks in order and use the saved preprocessing artifacts from data/processed/.
- Environment: see model_metadata_v1.0.0.json for recorded Python & package versions.

## Release checklist

- [ ] model metadata attached (artifacts/model_metadata_v1.0.0.json)
- [ ] artifact checksum attached (artifacts/telco-model-v1.0.0.sha256)
- [ ] integration tests passed (load ONNX and run sample inferences)
- [ ] performance validated on holdout set (refer to data/result/)
- [ ] release tagged and published
