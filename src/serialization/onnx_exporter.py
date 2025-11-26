"""
ONNX Exporter - Converts models to ONNX format
"""

import onnx
from typing import List
from catboost import CatBoostClassifier


class ONNXExporter:
    """
    Responsible for exporting models to ONNX format
    """
    
    @staticmethod
    def export_to_onnx(model: CatBoostClassifier,
                       onnx_path: str,
                       feature_names: List[str]) -> bool:
        """
        Export CatBoost model to ONNX format
        
        Args:
            model: Trained CatBoost model
            onnx_path: Path to save ONNX file
            feature_names: List of feature names
            
        Returns:
            True if successful
        """
        try:
            model.save_model(
                onnx_path,
                format='onnx',
                export_parameters={'feature_names': feature_names}
            )
            return True
        except Exception as e:
            print(f"ONNX export failed: {e}")
            return False
    
    @staticmethod
    def validate_onnx(onnx_path: str) -> bool:
        """
        Validate ONNX model
        
        Args:
            onnx_path: Path to ONNX file
            
        Returns:
            True if valid
        """
        try:
            onnx_model = onnx.load(onnx_path)
            onnx.checker.check_model(onnx_model)
            return True
        except Exception as e:
            print(f"ONNX validation failed: {e}")
            return False
