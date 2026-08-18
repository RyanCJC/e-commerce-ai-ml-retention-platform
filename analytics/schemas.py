from pydantic import BaseModel


class AnalyticsOverview(BaseModel):

    total_customers: int
    predicted_churn_rate: float
    average_churn_probability: float


class AnalyticsResponse(BaseModel):

    overview: AnalyticsOverview
    risk_distribution: dict
    risk_segment_summary: dict
    customer_metrics_by_risk: dict
    top_risk_factors: list
    risk_factors_by_risk_level: dict


class CustomerAnalytics(BaseModel):
    customer_id: int
    churn_prediction: int
    churn_probability: float
    risk_level: str

    frequency: int
    monetary: float
    avg_order_value: float

    unique_categories: int
    unique_sellers: int

    avg_review_score: float
    late_delivery_ratio: float

class CustomerDetailResponse(BaseModel):
    customer: dict
    latest_analysis: dict | None