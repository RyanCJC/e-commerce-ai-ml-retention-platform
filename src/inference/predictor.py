import mlflow
import mlflow.sklearn
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path("../").resolve()

mlflow.set_tracking_uri(
    f"sqlite:///{PROJECT_ROOT / 'mlflow.db'}"
)

MODEL_NAME = "CustomerChurnLightGBM"
MODEL_VERSION = "1"

MODEL_URI = f"models:/{MODEL_NAME}/{MODEL_VERSION}"

model = mlflow.sklearn.load_model(MODEL_URI)


def get_risk_level(probability: float) -> str:
    if probability >= 0.70:
        return "High"
    if probability >= 0.40:
        return "Medium"
    return "Low"

def predict_churn(customer_data: dict) -> dict:
    input_df = pd.DataFrame([customer_data])

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0, 1]

    return {
        "churn_prediction": int(prediction),
        "churn_probability": float(probability),
        "risk_level": get_risk_level(float(probability))
    }