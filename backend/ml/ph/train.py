from __future__ import annotations

from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

OUTPUT_DIR = Path(__file__).parent
DATASET_PATH = OUTPUT_DIR / "ph_correction_dataset.csv"

LIME_MODEL_PATH = OUTPUT_DIR / "lime_model.pkl"
SULPHUR_MODEL_PATH = OUTPUT_DIR / "sulphur_model.pkl"
METADATA_PATH = OUTPUT_DIR / "model_metadata.pkl"


def load_dataset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    if "current_ph" in df.columns and "ph" not in df.columns:
        df = df.rename(columns={"current_ph": "ph"})

    required_columns = {"ph", "amendment_type", "amendment_kg_per_acre"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["ph"] = pd.to_numeric(df["ph"], errors="coerce")
    df["amendment_kg_per_acre"] = pd.to_numeric(df["amendment_kg_per_acre"], errors="coerce")

    df = df.dropna(subset=["ph", "amendment_type", "amendment_kg_per_acre"])
    df = df[(df["ph"] >= 0) & (df["ph"] <= 14)]
    df = df[df["amendment_kg_per_acre"] >= 0]

    if df.empty:
        raise ValueError("Dataset is empty after cleaning.")

    return df


def train_single_model(df: pd.DataFrame, label: str) -> tuple[Ridge, dict]:
    X = df[["ph"]]
    y = df["amendment_kg_per_acre"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    metrics = {
        "label": label,
        "rows": len(df),
        "mae": float(mean_absolute_error(y_test, preds)),
        "r2": float(r2_score(y_test, preds)),
    }

    return model, metrics


def train() -> None:
    print("[PH CORRECTION MODEL TRAINING]")

    df = load_dataset(DATASET_PATH)
    print(f"Loaded dataset with {len(df)} rows")

    lime_df = df[df["amendment_type"].str.lower() == "lime"].copy()
    sulphur_df = df[df["amendment_type"].str.lower() == "sulphur"].copy()

    if len(lime_df) < 10:
        raise ValueError("Not enough lime rows to train model.")
    if len(sulphur_df) < 10:
        raise ValueError("Not enough sulphur rows to train model.")

    lime_model, lime_metrics = train_single_model(lime_df, "lime")
    sulphur_model, sulphur_metrics = train_single_model(sulphur_df, "sulphur")

    joblib.dump(lime_model, LIME_MODEL_PATH)
    joblib.dump(sulphur_model, SULPHUR_MODEL_PATH)

    metadata = {
        "approach": "two_model_regression",
        "input_feature": ["ph"],
        "output_target": "amendment_kg_per_acre",
        "lime_metrics": lime_metrics,
        "sulphur_metrics": sulphur_metrics,
    }
    joblib.dump(metadata, METADATA_PATH)

    print("\n[LIME MODEL]")
    print(f"Rows: {lime_metrics['rows']}")
    print(f"MAE: {lime_metrics['mae']:.2f}")
    print(f"R²:  {lime_metrics['r2']:.3f}")

    print("\n[SULPHUR MODEL]")
    print(f"Rows: {sulphur_metrics['rows']}")
    print(f"MAE: {sulphur_metrics['mae']:.2f}")
    print(f"R²:  {sulphur_metrics['r2']:.3f}")

    print(f"\nSaved: {LIME_MODEL_PATH}")
    print(f"Saved: {SULPHUR_MODEL_PATH}")
    print(f"Saved: {METADATA_PATH}")


if __name__ == "__main__":
    train()