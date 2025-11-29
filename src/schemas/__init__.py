"""
Shared data schemas for the application
"""

from .model_schemas import PredictRequest, PredictResponse, TrainingData

__all__ = ["PredictRequest", "PredictResponse", "TrainingData"]
