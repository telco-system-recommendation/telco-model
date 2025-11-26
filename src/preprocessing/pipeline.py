"""
Preprocessing Pipeline - Handles all data transformation logic
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List
from sklearn.preprocessing import StandardScaler, LabelEncoder


class PreprocessingPipeline:
    """
    Handles all preprocessing steps:
    - Outlier removal (IQR method)
    - Negative value removal
    - Categorical encoding
    - Feature scaling
    """
    
    def __init__(self, 
                 scaler: StandardScaler,
                 label_encoder: LabelEncoder,
                 feature_names: List[str]):
        self.scaler = scaler
        self.label_encoder = label_encoder
        self.feature_names = feature_names
    
    def remove_outliers_iqr(self, df: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """
        Remove outliers using IQR method
        
        Args:
            df: Feature dataframe
            y: Target series (optional)
            
        Returns:
            Cleaned dataframe and target series
        """
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        mask = pd.Series([True] * len(df))
        
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            mask &= (df[col] >= lower_bound) & (df[col] <= upper_bound)
        
        df_clean = df[mask].copy()
        y_clean = y[mask].copy() if y is not None else None
        
        return df_clean, y_clean
    
    def remove_negative_values(self, df: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """
        Remove rows with negative numeric values
        
        Args:
            df: Feature dataframe
            y: Target series (optional)
            
        Returns:
            Cleaned dataframe and target series
        """
        num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if len(num_cols) > 0:
            mask = ~(df[num_cols] < 0).any(axis=1)
            df_clean = df[mask].copy()
            y_clean = y[df_clean.index].copy() if y is not None else None
        else:
            df_clean = df.copy()
            y_clean = y.copy() if y is not None else None
        
        return df_clean, y_clean
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        One-hot encode categorical features
        
        Args:
            df: Feature dataframe
            
        Returns:
            Encoded dataframe
        """
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        # Align columns with training features
        for col in self.feature_names:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        
        # Ensure column order matches training
        df_encoded = df_encoded[self.feature_names]
        
        return df_encoded
    
    def scale_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Scale features using fitted scaler
        
        Args:
            df: Feature dataframe
            
        Returns:
            Scaled feature array
        """
        return self.scaler.transform(df)
    
    def encode_target(self, y: pd.Series) -> np.ndarray:
        """
        Encode target labels
        
        Args:
            y: Target series
            
        Returns:
            Encoded target array
        """
        return self.label_encoder.transform(y)
    
    def preprocess_new_data(self, df: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Full preprocessing pipeline for new data
        
        Args:
            df: Raw dataframe with features and optional target
            
        Returns:
            Tuple of (X_scaled, y_encoded)
        """
        # Remove customer_id if exists
        if 'customer_id' in df.columns:
            df = df.drop('customer_id', axis=1)
        
        # Separate target if exists
        y = None
        if 'target_offer' in df.columns:
            y = df['target_offer'].copy()
            df = df.drop('target_offer', axis=1)
        
        # Clean data
        df, y = self.remove_outliers_iqr(df, y)
        df, y = self.remove_negative_values(df, y)
        
        if len(df) == 0:
            return None, None
        
        # Encode and scale
        df_encoded = self.encode_categorical(df)
        X_scaled = self.scale_features(df_encoded)
        
        # Encode target if exists
        y_encoded = None
        if y is not None and len(y) > 0:
            y_encoded = self.encode_target(y)
        
        return X_scaled, y_encoded
