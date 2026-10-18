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
from pydantic import BaseModel, Field, model_validator

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
State = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

PaymentType = Literal["credit_card", "boleto", "voucher", "debit_card"]

STATE_BOUNDS = {
    "AC": (-11.15, -7.11, -73.99, -66.62), "AL": (-10.50, -8.81, -38.24, -35.15),
    "AP": (-1.24, 4.44, -54.88, -49.88),   "AM": (-9.82, 2.25, -73.80, -56.10),
    "BA": (-18.35, -8.53, -46.62, -37.34), "CE": (-7.86, -2.78, -41.42, -37.25),
    "DF": (-16.05, -15.50, -48.29, -47.31), "ES": (-21.30, -17.89, -41.88, -39.69),
    "GO": (-19.50, -12.39, -53.25, -45.91), "MA": (-10.26, -1.04, -48.76, -41.80),
    "MT": (-18.04, -7.35, -61.63, -50.22), "MS": (-24.07, -17.17, -58.17, -50.92),
    "MG": (-22.92, -14.23, -51.05, -39.86), "PA": (-9.84, 2.59, -58.90, -46.06),
    "PB": (-8.30, -6.02, -38.77, -34.79),  "PR": (-26.72, -22.52, -54.62, -48.02),
    "PE": (-9.48, -7.15, -41.36, -34.81),  "PI": (-10.93, -2.74, -45.99, -40.37),
    "RJ": (-23.37, -20.76, -44.89, -40.96), "RN": (-6.98, -4.83, -38.58, -34.97),
    "RS": (-33.75, -27.08, -57.65, -49.69), "RO": (-13.69, -7.97, -66.81, -59.77),
    "RR": (-1.58, 5.27, -64.83, -58.89),   "SC": (-29.35, -25.96, -53.84, -48.36),
    "SP": (-25.31, -19.78, -53.11, -44.16), "SE": (-11.57, -9.51, -38.25, -36.39),
    "TO": (-13.47, -5.17, -50.74, -45.70),
}
BOUNDS_MARGIN = 0.25


class CustomerInput(BaseModel):
    frequency: int = Field(ge=1, le=100)
    monetary: float = Field(gt=0, le=100_000)
    avg_order_value: float = Field(gt=0, le=100_000)
    unique_categories: int = Field(ge=1, le=71)
    unique_sellers: int = Field(ge=1, le=100)
    avg_review_score: float = Field(ge=1, le=5)
    late_delivery_ratio: float = Field(ge=0, le=1)
    avg_installments: float = Field(ge=1, le=24)
    max_installments: float = Field(ge=1, le=24)
    payment_method_count: int = Field(ge=1, le=4)
    preferred_payment_type: PaymentType
    state: State
    latitude: float = Field(ge=-34.0, le=5.5)
    longitude: float = Field(ge=-74.0, le=-34.0)

    @model_validator(mode="after")
    def validate_business_rules(self):
        errors = []

        expected_aov = self.monetary / self.frequency
        if abs(self.avg_order_value - expected_aov) > max(1.0, 0.01 * expected_aov):
            errors.append(
                f"avg_order_value should be about monetary / frequency "
                f"(expected ~{expected_aov:.2f})"
            )

        late_orders = round(self.late_delivery_ratio * self.frequency)
        if abs(late_orders / self.frequency - self.late_delivery_ratio) > 0.0051:
            errors.append(
                "late_delivery_ratio must equal (number of late orders / frequency) "
                f"for frequency={self.frequency}"
            )

        if self.frequency == 1 and self.avg_review_score != int(self.avg_review_score):
            errors.append("With a single purchase, avg_review_score must be a whole number")

        if self.avg_installments > self.max_installments:
            errors.append("avg_installments cannot be greater than max_installments")
        if self.frequency == 1 and self.avg_installments != self.max_installments:
            errors.append("With a single purchase, avg_installments must equal max_installments")

        if (
            self.payment_method_count == 1
            and self.preferred_payment_type != "credit_card"
            and self.max_installments != 1
        ):
            errors.append(
                "A customer using only boleto, voucher or debit card "
                "cannot have installments above 1"
            )

        lat_min, lat_max, lon_min, lon_max = STATE_BOUNDS[self.state]
        margin = BOUNDS_MARGIN
        if not (
            lat_min - margin <= self.latitude <= lat_max + margin
            and lon_min - margin <= self.longitude <= lon_max + margin
        ):
            errors.append(f"latitude/longitude fall outside the state {self.state}")

        if errors:
            raise ValueError("; ".join(errors))
        return self

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
        traceback.print_exc()
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

# Use python -m api.main