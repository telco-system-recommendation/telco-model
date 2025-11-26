"""
Artifact Manager - Handles saving, loading, and versioning of models
"""

import os
import joblib
import shutil
from datetime import datetime
from typing import Optional, List
from pathlib import Path


class ArtifactManager:
    """
    Responsible for saving, loading, and backing up model artifacts
    Supports versioning and backup management
    """
    
    def __init__(self,
                 model_dir: str = '../model',
                 backup_dir: str = '../data/retrain/backups',
                 log_dir: str = '../data/retrain/logs'):
        self.model_dir = model_dir
        self.backup_dir = backup_dir
        self.log_dir = log_dir
        
        # Create directories
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
    
    def save_model(self, model, model_path: str) -> bool:
        """
        Save model to disk
        
        Args:
            model: Model object
            model_path: Path to save model
            
        Returns:
            True if successful
        """
        try:
            joblib.dump(model, model_path)
            return True
        except Exception as e:
            print(f"Failed to save model: {e}")
            return False
    
    def load_model(self, model_path: str):
        """
        Load model from disk
        
        Args:
            model_path: Path to model file
            
        Returns:
            Loaded model or None if failed
        """
        if not os.path.exists(model_path):
            print(f"Model not found: {model_path}")
            return None
        
        try:
            return joblib.load(model_path)
        except Exception as e:
            print(f"Failed to load model: {e}")
            return None
    
    def backup_model(self, model_path: str, timestamp: Optional[str] = None) -> Optional[str]:
        """
        Create backup of existing model
        
        Args:
            model_path: Path to model to backup
            timestamp: Optional timestamp string, generated if not provided
            
        Returns:
            Backup file path or None if failed
        """
        if not os.path.exists(model_path):
            print(f"Model not found for backup: {model_path}")
            return None
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        model_name = os.path.basename(model_path)
        name_parts = os.path.splitext(model_name)
        backup_name = f"{name_parts[0]}_backup_{timestamp}{name_parts[1]}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(model_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Backup failed: {e}")
            return None
    
    def list_backups(self, pattern: str = "*_backup_*") -> List[str]:
        """
        List all backup files
        
        Args:
            pattern: Glob pattern for backup files
            
        Returns:
            List of backup file paths
        """
        backup_path = Path(self.backup_dir)
        return sorted([str(p) for p in backup_path.glob(pattern)], reverse=True)
    
    def cleanup_old_backups(self, keep_latest: int = 5):
        """
        Remove old backups, keeping only the most recent ones
        
        Args:
            keep_latest: Number of backups to keep
        """
        backups = self.list_backups()
        
        if len(backups) > keep_latest:
            for backup in backups[keep_latest:]:
                try:
                    os.remove(backup)
                    print(f"Removed old backup: {backup}")
                except Exception as e:
                    print(f"Failed to remove backup {backup}: {e}")
    
    def save_log(self, log_content: str, timestamp: Optional[str] = None) -> str:
        """
        Save retrain log
        
        Args:
            log_content: Log content to save
            timestamp: Optional timestamp, generated if not provided
            
        Returns:
            Path to log file
        """
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        log_filename = f"retrain_log_{timestamp}.txt"
        log_path = os.path.join(self.log_dir, log_filename)
        
        with open(log_path, 'w') as f:
            f.write(log_content)
        
        return log_path
    
    def get_model_version(self, model_path: str) -> str:
        """
        Get version info for a model (based on modification time)
        
        Args:
            model_path: Path to model file
            
        Returns:
            Version string (timestamp)
        """
        if not os.path.exists(model_path):
            return "unknown"
        
        mtime = os.path.getmtime(model_path)
        return datetime.fromtimestamp(mtime).strftime('%Y%m%d_%H%M%S')
