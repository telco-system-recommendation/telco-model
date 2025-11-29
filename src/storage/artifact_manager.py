"""Artifact Manager - Handles saving, loading, and versioning of models."""

import joblib
import shutil
from datetime import datetime
from typing import Optional, List, Union
from pathlib import Path
from src.config import MODEL_DIR, BACKUP_DIR, LOG_DIR


class ArtifactManager:
    """Responsible for saving, loading, and backing up model artifacts."""
    
    def __init__(self,
                 model_dir: Union[str, Path] = MODEL_DIR,
                 backup_dir: Union[str, Path] = BACKUP_DIR,
                 log_dir: Union[str, Path] = LOG_DIR):
        self.model_dir = Path(model_dir)
        self.backup_dir = Path(backup_dir)
        self.log_dir = Path(log_dir)
        
        # Create directories
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def save_model(self, model, model_path: Union[str, Path]) -> bool:
        """
        Save model to disk
        
        Args:
            model: Model object
            model_path: Path to save model
            
        Returns:
            True if successful
        """
        try:
            joblib.dump(model, Path(model_path))
            return True
        except Exception as e:
            print(f"Failed to save model: {e}")
            return False
    
    def load_model(self, model_path: Union[str, Path]):
        """
        Load model from disk
        
        Args:
            model_path: Path to model file
            
        Returns:
            Loaded model or None if failed
        """
        model_path = Path(model_path)
        if not model_path.exists():
            print(f"Model not found: {model_path}")
            return None
        
        try:
            return joblib.load(model_path)
        except Exception as e:
            print(f"Failed to load model: {e}")
            return None
    
    def backup_model(self, model_path: Union[str, Path], timestamp: Optional[str] = None) -> Optional[str]:
        """
        Create backup of existing model
        
        Args:
            model_path: Path to model to backup
            timestamp: Optional timestamp string, generated if not provided
            
        Returns:
            Backup file path or None if failed
        """
        model_path = Path(model_path)
        if not model_path.exists():
            print(f"Model not found for backup: {model_path}")
            return None
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        model_name = model_path.stem
        backup_name = f"{model_name}_backup_{timestamp}{model_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(model_path, backup_path)
            return str(backup_path)
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
        return sorted([str(p) for p in self.backup_dir.glob(pattern)], reverse=True)
    
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
                    Path(backup).unlink()
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
        log_path = self.log_dir / log_filename
        
        with open(log_path, 'w') as f:
            f.write(log_content)
        
        return str(log_path)
    
    def get_model_version(self, model_path: str) -> str:
        """
        Get version info for a model (based on modification time)
        
        Args:
            model_path: Path to model file
            
        Returns:
            Version string (timestamp)
        """
        model_path = Path(model_path)
        if not model_path.exists():
            return "unknown"
        
        mtime = model_path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime('%Y%m%d_%H%M%S')
