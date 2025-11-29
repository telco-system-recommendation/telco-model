"""
Prediction Counter - Manages prediction counting for retrain triggers
"""

from pathlib import Path
from src.config import PREDICTION_COUNTER_PATH


class PredictionCounter:
    """
    Manages the prediction counter for determining when to retrain
    """
    
    def __init__(self, counter_path: Path = PREDICTION_COUNTER_PATH):
        self.counter_path = Path(counter_path)
        self._init_counter()
    
    def _init_counter(self):
        """Initialize counter file if it doesn't exist"""
        self.counter_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.counter_path.exists():
            with open(self.counter_path, 'w') as f:
                f.write('0')
    
    def get_count(self) -> int:
        """
        Get current prediction count
        
        Returns:
            Current count
        """
        with open(self.counter_path, 'r') as f:
            return int(f.read().strip())
    
    def increment(self, count: int = 1) -> int:
        """
        Increment counter by specified amount
        
        Args:
            count: Amount to increment
            
        Returns:
            New count value
        """
        current = self.get_count()
        new_count = current + count
        with open(self.counter_path, 'w') as f:
            f.write(str(new_count))
        return new_count
    
    def reset(self):
        """Reset counter to zero"""
        with open(self.counter_path, 'w') as f:
            f.write('0')
    
    def should_retrain(self, threshold: int) -> bool:
        """
        Check if retrain threshold is reached
        
        Args:
            threshold: Number of predictions before retraining
            
        Returns:
            True if threshold reached
        """
        return self.get_count() >= threshold
