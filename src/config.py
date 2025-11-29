"""Centralized paths and runtime configuration for the Telco model service."""

import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

# Base directories
ROOT_DIR: Final[Path] = Path(__file__).resolve().parents[1]
SRC_DIR: Final[Path] = ROOT_DIR / "src"
ENV_FILE_PATH: Final[Path] = ROOT_DIR / ".env"

# Load .env for local development (container orchestration should inject env vars)
load_dotenv(dotenv_path=ENV_FILE_PATH, override=False)

def _resolve_path(env_key: str, default: Path) -> Path:
    return Path(os.getenv(env_key, str(default))).expanduser().resolve()


DATA_DIR: Final[Path] = _resolve_path("DATA_DIR", ROOT_DIR / "data")
MODEL_DIR: Final[Path] = _resolve_path("MODEL_DIR", ROOT_DIR / "model")

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

# Runtime configuration
API_HOST: Final[str] = os.getenv("API_HOST", "0.0.0.0")
API_PORT: Final[int] = int(os.getenv("API_PORT", "8000"))
API_WORKERS: Final[int] = int(os.getenv("API_WORKERS", "1"))
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: Final[str] = os.getenv("LOG_FORMAT", "text")
RETRAIN_THRESHOLD: Final[int] = int(os.getenv("RETRAIN_THRESHOLD", "1000"))
AUTO_RETRAIN_ENABLED: Final[bool] = os.getenv("AUTO_RETRAIN_ENABLED", "true").lower() == "true"

__all__ = [
    "ROOT_DIR",
    "SRC_DIR",
    "ENV_FILE_PATH",
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
    "API_HOST",
    "API_PORT",
    "API_WORKERS",
    "LOG_LEVEL",
    "LOG_FORMAT",
    "RETRAIN_THRESHOLD",
    "AUTO_RETRAIN_ENABLED",
]
