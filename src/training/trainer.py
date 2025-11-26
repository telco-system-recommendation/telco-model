"""
Model Trainer - Handles model training and evaluation
"""

import numpy as np
from typing import Tuple, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE
from catboost import CatBoostClassifier


class ModelTrainer:
    """
    Responsible for training and evaluating models
    """
    
    def __init__(self, 
                 model_params: Dict[str, Any] = None,
                 smote_params: Dict[str, Any] = None):
        """
        Initialize trainer with model parameters
        
        Args:
            model_params: CatBoost hyperparameters
            smote_params: SMOTE parameters
        """
        self.model_params = model_params or {
            'iterations': 600,
            'learning_rate': 0.1,
            'depth': 6,
            'loss_function': 'MultiClass',
            'eval_metric': 'TotalF1',
            'random_seed': 42,
            'grow_policy': 'SymmetricTree',
            'early_stopping_rounds': 40,
            'l2_leaf_reg': 5,
            'random_strength': 1.2,
            'colsample_bylevel': 0.8,
            'task_type': 'CPU',
            'verbose': False
        }
        
        self.smote_params = smote_params or {
            'random_state': 42,
            'k_neighbors': 5
        }
    
    def apply_smote(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply SMOTE to balance classes
        
        Args:
            X: Feature array
            y: Target array
            
        Returns:
            Balanced X and y
        """
        smote = SMOTE(**self.smote_params)
        X_balanced, y_balanced = smote.fit_resample(X, y)
        return X_balanced, y_balanced
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray) -> CatBoostClassifier:
        """
        Train CatBoost model
        
        Args:
            X_train: Training features
            y_train: Training labels
            
        Returns:
            Trained model
        """
        model = CatBoostClassifier(**self.model_params)
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, 
                      model: CatBoostClassifier, 
                      X_val: np.ndarray, 
                      y_val: np.ndarray,
                      label_encoder: Any) -> Dict[str, Any]:
        """
        Evaluate model performance
        
        Args:
            model: Trained model
            X_val: Validation features
            y_val: Validation labels
            label_encoder: Label encoder for class names
            
        Returns:
            Dictionary with evaluation metrics
        """
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)
        
        f1_weighted = f1_score(y_val, y_pred, average='weighted')
        f1_macro = f1_score(y_val, y_pred, average='macro')
        
        try:
            auc = roc_auc_score(y_val, y_pred_proba, multi_class='ovr')
        except:
            auc = None
        
        class_report = classification_report(
            y_val, y_pred, 
            target_names=label_encoder.classes_
        )
        
        return {
            'f1_weighted': f1_weighted,
            'f1_macro': f1_macro,
            'roc_auc': auc,
            'classification_report': class_report
        }
    
    def train_and_evaluate(self,
                          X: np.ndarray,
                          y: np.ndarray,
                          label_encoder: Any,
                          apply_balancing: bool = True,
                          test_size: float = 0.2) -> Tuple[CatBoostClassifier, Dict[str, Any]]:
        """
        Complete training pipeline with evaluation
        
        Args:
            X: Feature array
            y: Target array
            label_encoder: Label encoder
            apply_balancing: Whether to apply SMOTE
            test_size: Validation set size
            
        Returns:
            Tuple of (trained_model, metrics)
        """
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42,
            stratify=y
        )
        
        # Apply SMOTE if requested
        if apply_balancing:
            X_train, y_train = self.apply_smote(X_train, y_train)
        
        # Train model
        model = self.train_model(X_train, y_train)
        
        # Evaluate
        metrics = self.evaluate_model(model, X_val, y_val, label_encoder)
        
        return model, metrics
