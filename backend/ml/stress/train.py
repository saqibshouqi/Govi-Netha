"""
COMPONENT 4 — Crop Stress ML Model Training
Owner: Roshana

Model: Random Forest Classifier
Task:  Predict crop stress risk level from environmental averages
Input: [avg_temperature, avg_humidity, avg_moisture, max_temperature]
Output: "low" | "medium" | "high"

Run: python backend/ml/stress/train.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "model.pkl"

def stress_label(avg_temp, avg_hum, avg_mois, max_temp):
    score = 0
    if avg_temp > 38 or max_temp > 42: score += 3
    elif avg_temp > 35:                 score += 2
    elif avg_temp > 32:                 score += 1
    if avg_hum < 40:   score += 2
    elif avg_hum < 55: score += 1
    if avg_mois < 30:  score += 2
    elif avg_mois < 45:score += 1
    if score >= 5:   return "high"
    if score >= 2:   return "medium"
    return "low"

def generate_synthetic_data(n: int = 700) -> pd.DataFrame:
    np.random.seed(99)
    avg_temp = np.random.uniform(18, 45, n)
    avg_hum  = np.random.uniform(30, 95, n)
    avg_mois = np.random.uniform(20, 90, n)
    max_temp = avg_temp + np.random.uniform(0, 5, n)
    labels   = [stress_label(avg_temp[i], avg_hum[i], avg_mois[i], max_temp[i]) for i in range(n)]
    return pd.DataFrame({
        "avg_temperature": avg_temp, "avg_humidity": avg_hum,
        "avg_moisture": avg_mois,   "max_temperature": max_temp,
        "label": labels,
    })

def train():
    df = generate_synthetic_data()
    X = df[["avg_temperature", "avg_humidity", "avg_moisture", "max_temperature"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("[STRESS MODEL]")
    print(classification_report(y_test, model.predict(X_test)))

    joblib.dump(model, OUTPUT_PATH)
    print(f"  Model saved → {OUTPUT_PATH}")

if __name__ == "__main__":
    train()
