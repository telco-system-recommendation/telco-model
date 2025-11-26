"""
Example usage of the Retrain Manager
Demonstrates how to log predictions and trigger retraining
"""

import numpy as np
import pandas as pd
from retrain import RetrainManager

def simulate_predictions():
    """
    Simulate 1100 predictions to trigger retraining
    """
    # Initialize manager
    manager = RetrainManager(retrain_threshold=1000)
    
    print(f"Starting simulation. Current count: {manager.get_prediction_count()}")
    print(f"Threshold: {manager.retrain_threshold}")
    
    # Load sample data for simulation
    df = pd.read_csv('../data/raw/data_capstone.csv')
    
    # Sample 1100 rows
    sample_data = df.sample(n=min(1100, len(df)), random_state=42)
    
    print(f"\nSimulating {len(sample_data)} predictions...")
    
    for idx, row in sample_data.iterrows():
        # Create feature dictionary (raw features before encoding)
        features_dict = {
            'monthly_spend': row['monthly_spend'],
            'avg_data_usage_gb': row['avg_data_usage_gb'],
            'pct_video_usage': row['pct_video_usage'],
            'avg_call_duration': row['avg_call_duration'],
            'sms_freq': row['sms_freq'],
            'topup_freq': row['topup_freq'],
            'travel_score': row['travel_score'],
            'complaint_count': row['complaint_count'],
            'plan_type': row['plan_type'],
            'device_brand': row['device_brand']
        }
        
        # Log prediction with true label
        triggered = manager.log_prediction(features_dict, row['target_offer'])
        
        if triggered:
            print(f"\n🎉 Retraining triggered at prediction {idx + 1}!")
            break
        
        # Print progress every 100 predictions
        if (idx + 1) % 100 == 0:
            print(f"  Progress: {idx + 1}/{len(sample_data)} predictions logged")
    
    print(f"\nFinal count: {manager.get_prediction_count()}")


def check_status():
    """
    Check current retrain status
    """
    manager = RetrainManager()
    
    count = manager.get_prediction_count()
    threshold = manager.retrain_threshold
    remaining = threshold - count
    
    print("\n=== RETRAIN STATUS ===")
    print(f"Current predictions logged: {count}")
    print(f"Retrain threshold: {threshold}")
    print(f"Predictions until retrain: {remaining}")
    print(f"Progress: {count/threshold*100:.1f}%")


def manual_trigger():
    """
    Manually trigger retraining (useful for testing or scheduled jobs)
    """
    from retrain import manual_retrain
    
    print("Manually triggering retraining...")
    manual_retrain()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "simulate":
            simulate_predictions()
        elif command == "status":
            check_status()
        elif command == "trigger":
            manual_trigger()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python retrain_example.py [simulate|status|trigger]")
    else:
        print("Usage: python retrain_example.py [simulate|status|trigger]")
        print("\nCommands:")
        print("  simulate - Simulate predictions to trigger retrain")
        print("  status   - Check current retrain status")
        print("  trigger  - Manually trigger retraining")
