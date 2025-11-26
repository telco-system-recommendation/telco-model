"""
Pydantic schemas for API request/response and internal data structures
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np


class PredictRequest(BaseModel):
    """Request schema for prediction endpoint"""
    inputs: List[List[float]] = Field(..., description="Scaled feature values for prediction")
    raw_features: Optional[List[Dict[str, Any]]] = Field(None, description="Raw features for retraining")
    true_labels: Optional[List[str]] = Field(None, description="Ground truth labels for retraining")


class PredictResponse(BaseModel):
    """Response schema for prediction endpoint"""
    labels: Optional[List[int]] = Field(None, description="Predicted class labels")
    probabilities: Optional[List[List[float]]] = Field(None, description="Prediction probabilities")
    prediction_count: Optional[int] = Field(None, description="Current prediction count")


class TrainingData(BaseModel):
    """Internal schema for training data"""
    X: Any  # np.ndarray - Pydantic doesn't validate numpy arrays well
    y: Any  # np.ndarray
    
    class Config:
        arbitrary_types_allowed = True


class FeatureData(BaseModel):
    """Schema for raw feature dictionary"""
    monthly_spend: float
    avg_data_usage_gb: float
    pct_video_usage: float
    avg_call_duration: float
    sms_freq: int
    topup_freq: int
    travel_score: float
    complaint_count: int
    plan_type: str
    device_brand: str
    
    class Config:
        extra = 'allow'  # Allow additional fields


class RetrainResult(BaseModel):
    """Result of retraining operation"""
    success: bool
    timestamp: str
    new_samples: int
    total_samples: int
    f1_weighted: float
    f1_macro: float
    roc_auc: Optional[float] = None
    model_path: str
    onnx_path: str
