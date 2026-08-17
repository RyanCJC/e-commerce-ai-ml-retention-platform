from pydantic import BaseModel, Field


class RetentionRecommendation(BaseModel):
    risk_level: str = Field(
        description="Overall customer churn risk level."
    )
    explanation: str = Field(
        description="Explanation of the customer's churn risk."
    )
    key_risk_factors: list[str] = Field(
        description="Main factors contributing to the customer's churn risk."
    )
    recommended_actions: list[str] = Field(
        description="Practical actions that could be taken to improve customer retention."
    )