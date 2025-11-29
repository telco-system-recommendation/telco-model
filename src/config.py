"""Centralized paths and runtime configuration for the Telco model service."""

from pathlib import Path
from typing import Final

# Base directories
ROOT_DIR: Final[Path] = Path(__file__).resolve().parents[1]
SRC_DIR: Final[Path] = ROOT_DIR / "src"
DATA_DIR: Final[Path] = ROOT_DIR / "data"
MODEL_DIR: Final[Path] = ROOT_DIR / "model"

# Data sub-directories
PROCESSED_DATA_DIR: Final[Path] = DATA_DIR / "processed"
RETRAIN_DATA_DIR: Final[Path] = DATA_DIR / "retrain"

# Artifact paths
MODEL_PKL_PATH: Final[Path] = MODEL_DIR / "best_model.pkl"
MODEL_ONNX_PATH: Final[Path] = MODEL_DIR / "best_model.onnx"
PREDICTION_BUFFER_PATH: Final[Path] = RETRAIN_DATA_DIR / "prediction_buffer.csv"
PREDICTION_COUNTER_PATH: Final[Path] = RETRAIN_DATA_DIR / "prediction_counter.txt"
BACKUP_DIR: Final[Path] = RETRAIN_DATA_DIR / "backups"
LOG_DIR: Final[Path] = RETRAIN_DATA_DIR / "logs"

__all__ = [
    "ROOT_DIR",
    "SRC_DIR",
    "DATA_DIR",
    "MODEL_DIR",
    "PROCESSED_DATA_DIR",
    "RETRAIN_DATA_DIR",
    "MODEL_PKL_PATH",
    "MODEL_ONNX_PATH",
    "PREDICTION_BUFFER_PATH",
    "PREDICTION_COUNTER_PATH",
    "BACKUP_DIR",
    "LOG_DIR",
]
