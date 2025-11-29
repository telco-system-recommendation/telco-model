"""Integration-style tests for the FastAPI app."""

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.config import PROCESSED_DATA_DIR, DATA_DIR


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provide a TestClient instance with startup/shutdown lifecycle handling."""
    with TestClient(app) as test_client:
        yield test_client


def _load_scaled_sample() -> List[float]:
    sample_path = PROCESSED_DATA_DIR / "X_test.npy"
    if not sample_path.exists():
        pytest.skip("X_test.npy not found; cannot validate /predict with scaled inputs")
    data = np.load(sample_path)
    if data.size == 0:
        pytest.skip("X_test.npy is empty")
    return data[0].astype(np.float32).tolist()


def _load_raw_sample() -> dict:
    raw_path = DATA_DIR / "raw" / "data_capstone.csv"
    if not raw_path.exists():
        pytest.skip("Raw data file not available")
    df = pd.read_csv(raw_path)
    if df.empty:
        pytest.skip("Raw data file is empty")
    sample = df.iloc[0].to_dict()
    sample.pop("target_offer", None)
    return sample


def test_health_endpoint_reports_model(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["model_loaded"] is True
    assert payload["preprocessing_loaded"] is True


def test_predict_with_scaled_input(client: TestClient):
    sample = _load_scaled_sample()
    response = client.post("/predict", json={"inputs": [sample]})
    assert response.status_code == 200
    body = response.json()
    assert "prediction_count" in body
    assert body["labels"] is None or len(body["labels"]) == 1


def test_predict_with_raw_features(client: TestClient):
    raw_sample = _load_raw_sample()
    response = client.post("/predict", json={"raw_features": [raw_sample]})
    assert response.status_code == 200
    body = response.json()
    assert "prediction_count" in body