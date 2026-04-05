"""
COMPONENT 2 — NPK Deficiency ML Model Training
Owner: Januki

Model: Random Forest Classifier
Task:  Classify NPK state and recommend fertilizer action
Input: [nitrogen, phosphorus, potassium]
Output: class label — "balanced" | "apply_nitrogen" | "apply_phosphorus" |
        "apply_potassium" | "apply_npk"

Run: python backend/ml/npk/train.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "model.pkl"

LABEL_MAP = {
    "balanced":         (lambda n, p, k: n >= 50 and p >= 25 and k >= 100),
    "apply_nitrogen":   (lambda n, p, k: n < 50  and p >= 25 and k >= 100),
    "apply_phosphorus": (lambda n, p, k: n >= 50 and p < 25  and k >= 100),
    "apply_potassium":  (lambda n, p, k: n >= 50 and p >= 25 and k < 100),
    "apply_np":         (lambda n, p, k: n < 50  and p < 25  and k >= 100),
    "apply_npk":        (lambda n, p, k: n < 50  and p < 25  and k < 100),
}

def label(n, p, k):
    for lbl, fn in LABEL_MAP.items():
        if fn(n, p, k):
            return lbl
    return "apply_npk"

def generate_synthetic_data(n: int = 800) -> pd.DataFrame:
    """Replace with real MongoDB export data when available."""
    np.random.seed(0)
    nitrogen    = np.random.uniform(10, 150, n)
    phosphorus  = np.random.uniform(5,  100, n)
    potassium   = np.random.uniform(30, 250, n)
    labels      = [label(nitrogen[i], phosphorus[i], potassium[i]) for i in range(n)]
    return pd.DataFrame({"nitrogen": nitrogen, "phosphorus": phosphorus,
                         "potassium": potassium, "label": labels})

def train():
    df = generate_synthetic_data()
    X = df[["nitrogen", "phosphorus", "potassium"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("[NPK MODEL]")
    print(classification_report(y_test, preds))

    joblib.dump(model, OUTPUT_PATH)
    print(f"  Model saved → {OUTPUT_PATH}")

if __name__ == "__main__":
    train()
