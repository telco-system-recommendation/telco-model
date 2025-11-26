"""
Data ingestion module - handles data fetching and prediction counting
"""

from .repository import DataRepository
from .stats import PredictionCounter

__all__ = ["DataRepository", "PredictionCounter"]
