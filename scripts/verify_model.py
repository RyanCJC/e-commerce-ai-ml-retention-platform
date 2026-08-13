from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "churn_model.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

print(f"Loaded model: {type(model)}")

if not hasattr(model, "predict"):
    raise TypeError("Model does not have predict().")

if not hasattr(model, "predict_proba"):
    raise TypeError("Model does not have predict_proba().")

print("Model verification passed.")