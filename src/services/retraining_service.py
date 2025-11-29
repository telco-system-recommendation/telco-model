"""
Retraining Service - Orchestrates the entire retraining workflow
This is the GLUE that connects all modules
"""

import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
from src.data_ingestion.repository import DataRepository
from src.data_ingestion.stats import PredictionCounter
from src.preprocessing.pipeline import PreprocessingPipeline
from src.training.trainer import ModelTrainer
from src.serialization.onnx_exporter import ONNXExporter
from src.storage.artifact_manager import ArtifactManager
from src.schemas.model_schemas import RetrainResult
from src.config import MODEL_PKL_PATH, MODEL_ONNX_PATH


class RetrainingService:
    """
    Orchestrates the entire retraining workflow
    Coordinates between all modules to perform end-to-end retraining
    """
    
    def __init__(self,
                 model_path: Union[str, Path] = MODEL_PKL_PATH,
                 onnx_path: Union[str, Path] = MODEL_ONNX_PATH,
                 retrain_threshold: int = 1000):
        
        self.model_path = Path(model_path)
        self.onnx_path = Path(onnx_path)
        self.retrain_threshold = retrain_threshold
        
        # Initialize all components
        self.data_repo = DataRepository()
        self.counter = PredictionCounter()
        self.artifact_manager = ArtifactManager()
        
        # Load preprocessing artifacts
        scaler, label_encoder, feature_names = self.data_repo.load_preprocessing_artifacts()
        self.preprocessing = PreprocessingPipeline(scaler, label_encoder, feature_names)
        self.trainer = ModelTrainer()
        self.onnx_exporter = ONNXExporter()
        
        self.label_encoder = label_encoder
        self.feature_names = feature_names
    
    def log_prediction(self, features_dict: dict, true_label: Optional[str] = None) -> bool:
        """
        Log a new prediction and check if retraining should be triggered
        
        Args:
            features_dict: Dictionary of raw features
            true_label: Ground truth label
            
        Returns:
            True if retraining was triggered
        """
        # Append to buffer
        self.data_repo.append_to_buffer(features_dict, true_label)
        
        # Increment counter
        new_count = self.counter.increment()
        
        # Check threshold
        if self.counter.should_retrain(self.retrain_threshold):
            print(f"🔄 Retrain threshold reached ({new_count} predictions). Starting retraining...")
            result = self.retrain()
            return result.success
        
        return False
    
    def retrain(self) -> RetrainResult:
        """
        Execute complete retraining workflow
        
        Returns:
            RetrainResult with metrics and paths
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Step 1: Backup current model
            print("📦 Backing up current model...")
            backup_path = self.artifact_manager.backup_model(self.model_path, timestamp)
            if backup_path:
                print(f"✓ Backup saved: {backup_path}")
            
            # Step 2: Load original training data
            print("📊 Loading original training data...")
            X_train_original, y_train_original = self.data_repo.load_original_training_data()
            print(f"✓ Loaded {len(X_train_original)} original samples")
            
            # Step 3: Load new data from buffer
            print("📥 Loading prediction buffer...")
            df_new = self.data_repo.load_prediction_buffer()
            
            if df_new is None:
                error_msg = "⚠️ No new data found in buffer. Skipping retrain."
                print(error_msg)
                return RetrainResult(
                    success=False,
                    timestamp=timestamp,
                    new_samples=0,
                    total_samples=len(X_train_original),
                    f1_weighted=0.0,
                    f1_macro=0.0,
                    model_path=str(self.model_path),
                    onnx_path=str(self.onnx_path)
                )
            
            if 'target_offer' not in df_new.columns:
                error_msg = "⚠️ No target labels in buffer. Cannot retrain without ground truth."
                print(error_msg)
                return RetrainResult(
                    success=False,
                    timestamp=timestamp,
                    new_samples=len(df_new),
                    total_samples=len(X_train_original),
                    f1_weighted=0.0,
                    f1_macro=0.0,
                    model_path=str(self.model_path),
                    onnx_path=str(self.onnx_path)
                )
            
            print(f"✓ Found {len(df_new)} new samples in buffer")
            
            # Step 4: Preprocess new data
            print("🔄 Preprocessing new data...")
            X_new, y_new = self.preprocessing.preprocess_new_data(df_new)
            
            if X_new is None or y_new is None or len(X_new) == 0:
                error_msg = "⚠️ No valid data after preprocessing. Skipping retrain."
                print(error_msg)
                return RetrainResult(
                    success=False,
                    timestamp=timestamp,
                    new_samples=0,
                    total_samples=len(X_train_original),
                    f1_weighted=0.0,
                    f1_macro=0.0,
                    model_path=str(self.model_path),
                    onnx_path=str(self.onnx_path)
                )
            
            print(f"✓ Preprocessed {len(X_new)} valid samples")
            
            # Step 5: Combine data
            print("🔗 Combining original and new data...")
            X_combined = np.vstack([X_train_original, X_new])
            y_combined = np.concatenate([y_train_original, y_new])
            print(f"✓ Combined dataset: {len(X_combined)} samples")
            
            # Step 6: Train new model
            print("🚀 Training new model with SMOTE balancing...")
            new_model, metrics = self.trainer.train_and_evaluate(
                X_combined,
                y_combined,
                self.label_encoder,
                apply_balancing=True
            )
            
            print(f"\n📈 Training Results:")
            print(f"   F1-Weighted: {metrics['f1_weighted']:.4f}")
            print(f"   F1-Macro: {metrics['f1_macro']:.4f}")
            if metrics['roc_auc']:
                print(f"   ROC-AUC: {metrics['roc_auc']:.4f}")
            
            # Step 7: Save new model
            print("\n💾 Saving new model...")
            save_success = self.artifact_manager.save_model(new_model, self.model_path)
            if save_success:
                print(f"✓ Model saved: {self.model_path}")
            
            # Step 8: Export to ONNX
            print("📤 Exporting to ONNX...")
            onnx_success = self.onnx_exporter.export_to_onnx(
                new_model,
                str(self.onnx_path),
                self.feature_names
            )
            if onnx_success:
                print(f"✓ ONNX model saved: {self.onnx_path}")
            
            # Step 9: Update training data for next cycle
            print("💾 Updating training data for next cycle...")
            self.data_repo.save_training_data(X_combined, y_combined)
            print("✓ Training data updated")
            
            # Step 10: Log results
            log_content = f"""Retrain Timestamp: {timestamp}
New samples added: {len(X_new)}
Total training samples: {len(X_combined)}
F1-Weighted: {metrics['f1_weighted']:.4f}
F1-Macro: {metrics['f1_macro']:.4f}
ROC-AUC: {metrics['roc_auc']:.4f if metrics['roc_auc'] else 'N/A'}

Classification Report:
{metrics['classification_report']}
"""
            log_path = self.artifact_manager.save_log(log_content, timestamp)
            print(f"✓ Log saved: {log_path}")
            
            # Step 11: Cleanup
            print("\n🧹 Cleaning up...")
            self.data_repo.clear_buffer()
            self.counter.reset()
            self.artifact_manager.cleanup_old_backups(keep_latest=5)
            print("✓ Buffer cleared, counter reset, old backups cleaned")
            
            print("\n🎉 Retraining completed successfully!")
            
            return RetrainResult(
                success=True,
                timestamp=timestamp,
                new_samples=len(X_new),
                total_samples=len(X_combined),
                f1_weighted=metrics['f1_weighted'],
                f1_macro=metrics['f1_macro'],
                roc_auc=metrics['roc_auc'],
                model_path=str(self.model_path),
                onnx_path=str(self.onnx_path)
            )
            
        except Exception as e:
            error_msg = f"❌ Retraining failed: {str(e)}"
            print(error_msg)
            
            # Log error
            error_log = f"""Retrain Failed: {timestamp}
Error: {str(e)}
"""
            self.artifact_manager.save_log(error_log, timestamp)
            
            return RetrainResult(
                success=False,
                timestamp=timestamp,
                new_samples=0,
                total_samples=0,
                f1_weighted=0.0,
                f1_macro=0.0,
                model_path=str(self.model_path),
                onnx_path=str(self.onnx_path)
            )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current retraining status
        
        Returns:
            Dictionary with status information
        """
        count = self.counter.get_count()
        remaining = self.retrain_threshold - count
        progress = (count / self.retrain_threshold) * 100
        
        return {
            'current_count': count,
            'threshold': self.retrain_threshold,
            'remaining': remaining,
            'progress_percent': round(progress, 2),
            'model_version': self.artifact_manager.get_model_version(self.model_path)
        }
