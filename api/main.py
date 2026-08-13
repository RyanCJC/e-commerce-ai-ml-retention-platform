from pathlib import Path
import joblib

import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ============================================================
# PROJECT PATHS
# ============================================================
MODEL_NAME = "CustomerChurn_RF"
MODEL_VERSION = "1"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "churn_model.pkl"


# ============================================================
# LOAD MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )

print(f"Loading model from: {MODEL_PATH}")

try:
    model = joblib.load(MODEL_PATH)

    print(
        f"Successfully loaded model: "
        f"{type(model).__name__}"
    )

except Exception as e:
    raise RuntimeError(
        f"Failed to load model from "
        f"'{MODEL_PATH}'. Error: {e}"
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="E-Commerce Customer Retention API",
    description="Customer churn prediction API using a registered Random Forest model.",
    version="1.0.0"
)


# ============================================================
# INPUT SCHEMA
# ============================================================

class CustomerInput(BaseModel):
    frequency: int
    monetary: float
    avg_order_value: float
    unique_categories: int
    unique_sellers: int
    avg_review_score: float
    late_delivery_ratio: float
    avg_installments: float
    max_installments: float
    payment_method_count: int
    preferred_payment_type: str
    state: str
    latitude: float
    longitude: float


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION
    }


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Customer Retention API is running",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict(customer: CustomerInput):
    try:
        customer_data = customer.model_dump()
        input_data = pd.DataFrame([customer_data])

        prediction = int(model.predict(input_data)[0])
        churn_probability = float(model.predict_proba(input_data)[0, 1])

        if churn_probability >= 0.70:
            risk_level = "High Churn Risk"
        elif churn_probability >= 0.40:
            risk_level = "Medium Churn Risk"
        else:
            risk_level = "Low Churn Risk"

        return {
            "churn_prediction": prediction,
            "churn_probability": round(churn_probability, 4),
            "risk_level": risk_level,
            # "model": MODEL_NAME,
            # "model_version": MODEL_VERSION
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )