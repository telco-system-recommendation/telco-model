"""FastAPI application for serving ML model predictions and retraining."""

import logging
from typing import Optional

import numpy as np
import onnxruntime as ort
import uvicorn
from fastapi import FastAPI, HTTPException
from src.schemas.model_schemas import PredictRequest, PredictResponse
from src.services.retraining_service import RetrainingService
from src.preprocessing.pipeline import PreprocessingPipeline
from src.config import (
    MODEL_ONNX_PATH,
    MODEL_PKL_PATH,
    RETRAIN_THRESHOLD,
    LOG_LEVEL,
    LOG_FORMAT,
    AUTO_RETRAIN_ENABLED,
    API_HOST,
    API_PORT,
    API_WORKERS,
)

# App state
class AppState:
    def __init__(self):
        self.session: Optional[ort.InferenceSession] = None
        self.retraining_service: Optional[RetrainingService] = None
        self.preprocessing: Optional[PreprocessingPipeline] = None

LOG_FORMAT_MAP = {
    "json": "{\"timestamp\":\"%(asctime)s\",\"level\":\"%(levelname)s\",\"name\":\"%(name)s\",\"message\":\"%(message)s\"}"
}

def _configure_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    fmt = LOG_FORMAT_MAP.get(LOG_FORMAT.lower(), "%(asctime)s %(levelname)s [%(name)s] %(message)s")
    logging.basicConfig(level=level, format=fmt)


_configure_logging()

app = FastAPI(title="Telco Offer Prediction API", version="2.0.0")
state = AppState()
logger = logging.getLogger("telco-model.api")

@app.on_event("startup")
async def startup_event():
    """Load ONNX model and initialize retraining service on startup"""
    model_path = str(MODEL_ONNX_PATH)
    logger.info("Loading ONNX model from %s", model_path)
    state.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    logger.info("Initializing retraining service (threshold=%s)", RETRAIN_THRESHOLD)
    state.retraining_service = RetrainingService(
        model_path=MODEL_PKL_PATH,
        onnx_path=MODEL_ONNX_PATH,
        retrain_threshold=RETRAIN_THRESHOLD
    )
    state.preprocessing = state.retraining_service.preprocessing
    logger.info("Startup complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telco Offer Prediction API",
        "version": "2.0.0",
        "endpoints": {
            "POST /predict": "Get prediction for customer features",
            "GET /health": "Check API health",
            "GET /retrain/status": "Get retraining status"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    status = state.retraining_service.get_status() if state.retraining_service else {}
    return {
        "status": "healthy",
        "model_loaded": state.session is not None,
        "preprocessing_loaded": state.preprocessing is not None,
        "prediction_count": status.get('current_count', 0),
        "model_version": status.get('model_version', 'unknown'),
        "auto_retrain_enabled": AUTO_RETRAIN_ENABLED,
    }


@app.get("/retrain/status")
async def retrain_status():
    """Get current retraining status"""
    if state.retraining_service is None:
        raise HTTPException(status_code=503, detail="Retraining service not initialized")
    
    return state.retraining_service.get_status()

def prepare_input_matrix(request: PredictRequest) -> np.ndarray:
    """Resolve correct feature matrix from scaled inputs or raw feature payloads."""
    if request.inputs:
        return np.array(request.inputs, dtype=np.float32)
    if request.raw_features:
        pipeline = state.preprocessing or (state.retraining_service.preprocessing if state.retraining_service else None)
        if pipeline is None:
            raise HTTPException(status_code=503, detail="Preprocessing pipeline not available")
        try:
            features = pipeline.prepare_inference_features(request.raw_features)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return np.asarray(features, dtype=np.float32)
    raise HTTPException(status_code=400, detail="Either 'inputs' or 'raw_features' must be provided")


def seq_map_to_probs(seq_map):
    """Convert sequence map to probability array"""
    probs = []
    for item in seq_map:
        keys = sorted(item.keys(), key=int)
        probs.append([float(item[k]) for k in keys])
    return probs


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Predict customer offer preferences
    
    Args:
        request: PredictRequest with scaled inputs and optional raw features + labels
        
    Returns:
        PredictResponse with predictions and current count
    """
    if state.session is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare input
        input_data = prepare_input_matrix(request)
        input_name = state.session.get_inputs()[0].name
        
        # Run inference
        raw_out = state.session.run(None, {input_name: input_data})
        
        # Map outputs
        outs = {}
        out_meta = state.session.get_outputs()
        if isinstance(raw_out, (list, tuple)):
            for meta, val in zip(out_meta, raw_out):
                outs[meta.name] = val
        elif isinstance(raw_out, dict):
            outs = raw_out
        
        # Extract labels
        labels = None
        if "label" in outs:
            labels = np.array(outs["label"]).astype(int).tolist()
        else:
            for v in outs.values():
                if isinstance(v, np.ndarray):
                    labels = np.array(v).astype(int).tolist()
                    break
        
        # Extract probabilities
        probabilities = None
        if "probabilities" in outs:
            probs_raw = outs["probabilities"]
            if isinstance(probs_raw, np.ndarray):
                probabilities = np.array(probs_raw).tolist()
            else:
                probabilities = seq_map_to_probs(probs_raw)
        
        # Log predictions for retraining (if raw features provided)
        retrain_triggered = False
        if request.raw_features:
            if len(request.raw_features) != input_data.shape[0]:
                raise HTTPException(status_code=400, detail="raw_features length must match number of samples")
            if not AUTO_RETRAIN_ENABLED:
                logger.debug("raw_features provided but AUTO_RETRAIN_ENABLED is false; skipping logging")
            elif state.retraining_service:
                for i, features_dict in enumerate(request.raw_features):
                    true_label = None
                    if request.true_labels and i < len(request.true_labels):
                        true_label = request.true_labels[i]
                    triggered = state.retraining_service.log_prediction(features_dict, true_label)
                    if triggered:
                        retrain_triggered = True
            else:
                logger.warning("Retraining service unavailable; cannot log raw_features payload")
        
        # Reload model if retrain was triggered
        if retrain_triggered:
            logger.info("Retrain triggered. Reloading ONNX model")
            state.session = ort.InferenceSession(str(MODEL_ONNX_PATH), providers=["CPUExecutionProvider"])
            logger.info("Model reloaded successfully")
        
        # Get current prediction count
        prediction_count = None
        if state.retraining_service:
            status = state.retraining_service.get_status()
            prediction_count = status['current_count']
        
        return PredictResponse(
            labels=labels,
            probabilities=probabilities,
            prediction_count=prediction_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT, workers=API_WORKERS)
