"""
Model: Random Forest Regressor
Task:  Predict hours until next irrigation is needed
Input: [soil_moisture %, temperature °C, drying_rate %/hr]
Output: hours_until_irrigation_needed (float)

Run: python backend/ml/irrigation/train.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "model.pkl"

def generate_synthetic_data(n: int = 500) -> pd.DataFrame:
    """
    Generates synthetic training data.
    Can replace this with real sensor data if readings are sufficient.
    Export MongoDB data via: mongoexport --collection=sensor_readings
    """
    np.random.seed(42)
    moisture     = np.random.uniform(20, 95, n)
    temperature  = np.random.uniform(20, 42, n)
    drying_rate  = np.random.uniform(0.5, 4.0, n)

    # Ground truth: hours until moisture drops to 40%
    # Higher temp → faster drying → fewer hours
    hours = (moisture - 40) / (drying_rate * (1 + (temperature - 30) * 0.05))
    hours = np.clip(hours, 0, 48) + np.random.normal(0, 0.5, n)

    return pd.DataFrame({
        "moisture": moisture,
        "temperature": temperature,
        "drying_rate": drying_rate,
        "hours_until_irrigation": np.clip(hours, 0, 48),
    })

def train():
    df = generate_synthetic_data(600)
    # ↑ Replace with: df = pd.read_csv("your_real_data.csv")

    X = df[["moisture", "temperature", "drying_rate"]]
    y = df["hours_until_irrigation"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(f"[IRRIGATION MODEL]")
    print(f"  MAE:  {mean_absolute_error(y_test, preds):.2f} hours")
    print(f"  R²:   {r2_score(y_test, preds):.3f}")

    joblib.dump(model, OUTPUT_PATH)
    print(f"  Model saved → {OUTPUT_PATH}")

if __name__ == "__main__":
    train()
