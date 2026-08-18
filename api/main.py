from pathlib import Path
import joblib
from llm.schemas import RetentionRecommendation
from llm.llm_graph import graph, analyze_customer
from analytics.service import get_dashboard_analytics
from analytics.schemas import AnalyticsResponse, CustomerAnalytics, CustomerDetailResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, Optional
import traceback

import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing from .env")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# PROJECT PATHS
MODEL_NAME = "CustomerChurn_RF"
MODEL_VERSION = "1"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "churn_model.pkl"


# LOAD MODEL
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


# FASTAPI APPLICATION
app = FastAPI(
    title="E-Commerce Customer Retention API",
    description="Customer churn prediction API using a registered Random Forest model.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INPUT SCHEMA
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


# HEALTH CHECK
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION
    }


# ROOT ENDPOINT
@app.get("/")
def root():
    return {
        "message": "Customer Retention API is running",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION
    }


# PREDICTION ENDPOINT
@app.post("/analyze")
def analyze(customer: CustomerInput):

    try:
        # 1. Convert API input
        customer_data = customer.model_dump()

        existing_customer = (
            supabase
            .table("customers")
            .select("id")
            .match(customer_data)
            .limit(1)
            .execute()
        )

        if existing_customer.data:
            customer_id = existing_customer.data[0]["id"]
        else:
            customer_result = (
                supabase
                .table("customers")
                .insert(customer_data)
                .execute()
            )
            if not customer_result.data:
                raise RuntimeError(
                    "Failed to create customer record"
                )
            customer_id = customer_result.data[0]["id"]

        # 3. Run analysis on LangGraph
        result = analyze_customer(
            customer_data=customer_data,
            message="Explain this customer's churn risk and suggest practical retention actions."
        )

        # 4. Prepare analysis record
        churn_result = {
            "customer_id": customer_id,
            "churn_prediction": result["churn_prediction"],
            "churn_probability": result["churn_probability"],
            "risk_level": result["risk_level"],
            "feature_contributions": result["feature_contributions"],
            "recommendation": result["recommendation"].model_dump()
        }

        # 5. Save analysis
        supabase \
            .table("churn_analyses") \
            .insert(churn_result) \
            .execute()

        # 6. Return API response
        return result

    except Exception as e:

        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get(
    "/analytics",
    response_model=AnalyticsResponse
)
def analytics():

    try:

        return get_dashboard_analytics()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Analytics failed: {str(e)}"
        )


@app.get(
    "/analytics/customers",
    response_model=list[CustomerAnalytics]
)
def analytics_customers(
    risk_level: Optional[Literal["Low", "Medium", "High"]] = None,
    min_probability: Optional[float] = None,
    limit: int = 50
):

    try:

        if min_probability is not None:
            if not 0 <= min_probability <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="min_probability must be between 0 and 1"
                )

        if limit < 1 or limit > 500:
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 500"
            )

        query = (
            supabase
            .from_("churn_analyses")
            .select(
                """
                customer_id,
                churn_prediction,
                churn_probability,
                risk_level,
                customers (
                    frequency,
                    monetary,
                    avg_order_value,
                    unique_categories,
                    unique_sellers,
                    avg_review_score,
                    late_delivery_ratio
                )
                """
            )
        )

        if risk_level:
            query = query.eq(
                "risk_level",
                risk_level
            )

        if min_probability is not None:
            query = query.gte(
                "churn_probability",
                min_probability
            )

        result = (
            query
            .order(
                "churn_probability",
                desc=True
            )
            .limit(limit)
            .execute()
        )

        customers = []

        for row in result.data:

            customer = row["customers"]

            customers.append(
                {
                    "customer_id": row["customer_id"],
                    "churn_prediction": row["churn_prediction"],
                    "churn_probability": row["churn_probability"],
                    "risk_level": row["risk_level"],

                    "frequency": customer["frequency"],
                    "monetary": customer["monetary"],
                    "avg_order_value": customer["avg_order_value"],

                    "unique_categories": customer["unique_categories"],
                    "unique_sellers": customer["unique_sellers"],

                    "avg_review_score": customer["avg_review_score"],
                    "late_delivery_ratio": customer["late_delivery_ratio"]
                }
            )

        return customers

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Analytics customer query failed: {str(e)}"
        )


@app.get(
    "/analytics/customers/{customer_id}",
    response_model=CustomerDetailResponse
)
def analytics_customer_detail(customer_id: int):

    try:

        customer_result = (
            supabase
            .from_("customers")
            .select("*")
            .eq("id", customer_id)
            .single()
            .execute()
        )

        customer = customer_result.data

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        analysis_result = (
            supabase
            .from_("churn_analyses")
            .select("*")
            .eq("customer_id", customer_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        latest_analysis = (
            analysis_result.data[0]
            if analysis_result.data
            else None
        )

        return {
            "customer": customer,
            "latest_analysis": latest_analysis
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Customer detail query failed: {str(e)}"
        )