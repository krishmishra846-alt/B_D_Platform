import xgboost as xgb
import pandas as pd
import numpy as np

class TurnoutPredictor:
    def __init__(self):
        """Initializes and trains the baseline XGBoost turnout model."""
        # Using a standard classifier with logloss evaluation
        self.model = xgb.XGBClassifier(eval_metric='logloss')
        
        # Baseline training data representing typical donor behavior patterns
        # Features: [Distance_km, Age, Historical_Donations_Count, Telegram_Interaction_Rate]
        X_baseline = pd.DataFrame({
            'Distance_km': [1.5, 25.0, 5.0, 18.0, 2.0, 30.0],
            'Age': [22, 45, 30, 20, 28, 50],
            'Historical_Donations_Count': [2, 0, 5, 1, 3, 0],
            'Telegram_Interaction_Rate': [0.9, 0.1, 0.8, 0.3, 1.0, 0.0]
        })
        
        # Target: 1 (Attended) or 0 (Did Not Attend)
        # Closer distance, higher past donations, and high engagement = likely to attend
        y_baseline = np.array([1, 0, 1, 0, 1, 0]) 
        
        # Train the model on startup
        self.model.fit(X_baseline, y_baseline)
        print("XGBoost Turnout Engine Initialized & Trained.")

    def calculate_probability(self, distance_km: float, age: int, past_donations: int, engagement_rate: float) -> float:
        """
        Executes predict_proba() to generate an attendance percentage score.
        """
        features = pd.DataFrame({
            'Distance_km': [distance_km],
            'Age': [age],
            'Historical_Donations_Count': [past_donations],
            'Telegram_Interaction_Rate': [engagement_rate]
        })
        
        # Predict probability of class 1 (Attending)
        probability = self.model.predict_proba(features)[0][1]
        
        # Return as a percentage rounded to 2 decimal places
        return round(probability * 100, 2)

# Instantiate the engine so it can be imported by FastAPI
turnout_engine = TurnoutPredictor()