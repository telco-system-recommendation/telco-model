"""
Data Repository - Handles fetching data from various sources
"""
from typing import Tuple, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from src.config import PROCESSED_DATA_DIR, PREDICTION_BUFFER_PATH



class DataRepository:
    """
    Responsible for fetching data from various sources
    (CSV, SQL, API, etc.)
    """
    
    def __init__(self,
                 data_buffer_path: Path = PREDICTION_BUFFER_PATH,
                 processed_data_dir: Path = PROCESSED_DATA_DIR):
        self.data_buffer_path = Path(data_buffer_path)
        self.processed_data_dir = Path(processed_data_dir)
        
        # Create buffer directory if not exists
        self.data_buffer_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_original_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load original training data from processed files
        
        Returns:
            X_train: Training features
            y_train: Training labels
        """
        X_path = self.processed_data_dir / 'X_train_original.npy'
        y_path = self.processed_data_dir / 'y_train_original.npy'
        
        if not X_path.exists() or not y_path.exists():
            raise FileNotFoundError(f"Training data not found in {self.processed_data_dir}")
        
        X_train = np.load(X_path)
        y_train = np.load(y_path)
        
        return X_train, y_train
    
    def load_prediction_buffer(self) -> Optional[pd.DataFrame]:
        """
        Load accumulated predictions from buffer
        
        Returns:
            DataFrame with logged predictions or None if buffer doesn't exist
        """
        if not self.data_buffer_path.exists():
            return None
        
        return pd.read_csv(self.data_buffer_path)
    
    def append_to_buffer(self, features_dict: dict, true_label: Optional[str] = None):
        """
        Append a new prediction to the buffer
        
        Args:
            features_dict: Dictionary of raw features
            true_label: Ground truth label (if available)
        """
        df_new = pd.DataFrame([features_dict])
        if true_label is not None:
            df_new['target_offer'] = true_label
        
        if self.data_buffer_path.exists():
            df_buffer = pd.read_csv(self.data_buffer_path)
            df_buffer = pd.concat([df_buffer, df_new], ignore_index=True)
        else:
            df_buffer = df_new
        
        df_buffer.to_csv(self.data_buffer_path, index=False)
    
    def clear_buffer(self):
        """Remove the prediction buffer file"""
        if self.data_buffer_path.exists():
            self.data_buffer_path.unlink()
    
    def save_training_data(self, X: np.ndarray, y: np.ndarray):
        """
        Save training data for next retraining cycle
        
        Args:
            X: Training features
            y: Training labels
        """
        X_path = self.processed_data_dir / 'X_train_original.npy'
        y_path = self.processed_data_dir / 'y_train_original.npy'
        
        np.save(X_path, X)
        np.save(y_path, y)
    
    def load_preprocessing_artifacts(self) -> Tuple:
        """
        Load scaler, encoder, and feature names
        
        Returns:
            Tuple of (scaler, label_encoder, feature_names)
        """
        import pickle
        
        scaler_path = self.processed_data_dir / 'scaler.pkl'
        encoder_path = self.processed_data_dir / 'label_encoder.pkl'
        features_path = self.processed_data_dir / 'feature_names.pkl'
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        with open(encoder_path, 'rb') as f:
            label_encoder = pickle.load(f)
        
        with open(features_path, 'rb') as f:
            feature_names = pickle.load(f)
        
        return scaler, label_encoder, feature_names
