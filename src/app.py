"""
FastAPI application for serving ML model predictions
Integrated with modular retraining architecture
"""

from fastapi import FastAPI, HTTPException
import onnxruntime as ort
import numpy as np
from typing import Optional
import uvicorn

from app.schemas.model_schemas import PredictRequest, PredictResponse
from app.services.retraining_service import RetrainingService

# App state
class AppState:
    def __init__(self):
        self.session: Optional[ort.InferenceSession] = None
        self.retraining_service: Optional[RetrainingService] = None

app = FastAPI(title="Telco Offer Prediction API", version="2.0.0")
state = AppState()

@app.on_event("startup")
async def startup_event():
    """Load ONNX model and initialize retraining service on startup"""
    model_path = "../model/best_model.onnx"
    state.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    state.retraining_service = RetrainingService(
        model_path='../model/best_model.pkl',
        onnx_path=model_path,
        retrain_threshold=1000
    )
    print(f"Model loaded from {model_path}")
    print(f"Retraining service initialized (threshold: 1000 predictions)")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telco Offer Prediction API",
        "version": "2.0.0",
        "architecture": "Modular with loose coupling",
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
        "prediction_count": status.get('current_count', 0),
        "model_version": status.get('model_version', 'unknown')
    }


@app.get("/retrain/status")
async def retrain_status():
    """Get current retraining status"""
    if state.retraining_service is None:
        raise HTTPException(status_code=503, detail="Retraining service not initialized")
    
    return state.retraining_service.get_status()

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
        input_data = np.array(request.inputs, dtype=np.float32)
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
        if (request.raw_features is not None and 
            len(request.raw_features) == len(request.inputs)):
            
            for i, features_dict in enumerate(request.raw_features):
                true_label = None
                if request.true_labels and i < len(request.true_labels):
                    true_label = request.true_labels[i]
                
                # Log prediction and check if retrain triggered
                triggered = state.retraining_service.log_prediction(features_dict, true_label)
                if triggered:
                    retrain_triggered = True
        
        # Reload model if retrain was triggered
        if retrain_triggered:
            print("🔄 Reloading model after retraining...")
            model_path = "../model/best_model.onnx"
            state.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            print("✓ Model reloaded successfully")
        
        # Get current prediction count
        status = state.retraining_service.get_status()
        prediction_count = status['current_count']
        
        return PredictResponse(
            labels=labels,
            probabilities=probabilities,
            prediction_count=prediction_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
