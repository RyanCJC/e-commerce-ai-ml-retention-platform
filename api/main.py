from pathlib import Path
import joblib
from llm.schemas import RetentionRecommendation
from llm.llm_graph import graph, analyze_customer

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

class FeatureContribution(BaseModel):
    feature: str
    shap_value: float
    direction: str

class PredictionResponse(BaseModel):
    churn_prediction: int
    churn_probability: float
    risk_level: str
    feature_contributions: list[FeatureContribution]
    recommendation: RetentionRecommendation

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
@app.post("/analyze")
def analyze(customer: CustomerInput):

    try:

        customer_data = customer.model_dump()

        result = analyze_customer(
            customer_data=customer_data,
            message="Explain this customer's churn risk and suggest retention actions."
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )