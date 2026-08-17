from pydantic import BaseModel, Field
from typing import Literal

class UserIntent(BaseModel):
    intent: Literal[
        "risk_explanation",
        "retention_strategy",
        "action_plan",
        "general_analysis"
    ]

class RetentionRecommendation(BaseModel):
    risk_level: str = Field(
        description="Overall customer churn risk level."
    )
    explanation: str = Field(
        description="Explanation of the customer's churn risk."
    )
    key_model_factors: list[str] = Field(
        description="Main factors contributing to the customer's churn risk."
    )
    recommended_actions: list[str] = Field(
        description="Practical actions that could be taken to improve customer retention."
    )

