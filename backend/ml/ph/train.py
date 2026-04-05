"""
COMPONENT 3 — pH Correction ML Model Training
Owner: Ravisha

Model: Linear Regression (Ridge)
Task:  Predict amendment quantity (kg/acre) needed to reach pH 6.5
Input: [current_ph]
Output: kg_per_acre of lime (if acidic) or sulphur (if alkaline)

Run: python backend/ml/ph/train.py
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "model.pkl"

def generate_synthetic_data(n: int = 400) -> pd.DataFrame:
    """
    Based on agricultural lime requirement tables for tropical soils.
    Replace with field trial data for higher accuracy.
    """
    np.random.seed(7)
    ph = np.random.uniform(4.0, 8.5, n)

    # Lime requirement: ~500 kg/acre per 1 pH unit increase needed
    lime_needed = np.where(
        ph < 6.5,
        (6.5 - ph) * 500 + np.random.normal(0, 20, n),
        0.0
    )
    lime_needed = np.clip(lime_needed, 0, 1500)

    return pd.DataFrame({"ph": ph, "amendment_kg_per_acre": lime_needed})

def train():
    df = generate_synthetic_data()
    X = df[["ph"]]
    y = df["amendment_kg_per_acre"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("[PH MODEL]")
    print(f"  MAE: {mean_absolute_error(y_test, preds):.1f} kg/acre")
    print(f"  R²:  {r2_score(y_test, preds):.3f}")

    joblib.dump(model, OUTPUT_PATH)
    print(f"  Model saved → {OUTPUT_PATH}")

if __name__ == "__main__":
    train()
