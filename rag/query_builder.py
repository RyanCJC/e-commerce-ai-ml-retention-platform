def build_retention_query(
    customer_data: dict,
    churn_probability: float,
    risk_level: str,
    feature_contributions: list[dict],
    strategy_focus: str
) -> str:

    feature_text = "\n".join(
        f"- {item['feature']}: "
        f"{item['direction']}"
        for item in feature_contributions
    )

    query = f"""
    Find evidence-based customer retention strategies
    relevant to an e-commerce customer.

    Customer churn risk:
    - Risk level: {risk_level}
    - Churn probability: {churn_probability:.4f}

    Customer characteristics:
    - Purchase frequency: {customer_data.get("frequency")}
    - Monetary value: {customer_data.get("monetary")}
    - Average order value: {customer_data.get("avg_order_value")}
    - Unique categories: {customer_data.get("unique_categories")}
    - Unique sellers: {customer_data.get("unique_sellers")}
    - Average review score: {customer_data.get("avg_review_score")}
    - Late delivery ratio: {customer_data.get("late_delivery_ratio")}

    Important model-attributed factors:
    {feature_text}

    Focus specifically on:

    {strategy_focus}

    Retrieve practical, evidence-based retention strategies
    that can be applied to this customer profile.

    Prefer strategies supported by customer retention,
    customer relationship management, e-commerce,
    loyalty, engagement, or churn-related research.
    """

    return query

