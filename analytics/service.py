from analytics.queries import (
    get_total_customers,
    get_churn_rate,
    get_risk_distribution,
    get_average_churn_probability,
    get_risk_segment_summary,
    get_customer_metrics_by_risk,
    get_top_risk_factors,
    get_risk_factors_by_risk_level,
)   


def get_dashboard_analytics():

    return {

        "overview": {
            "total_customers": get_total_customers(),
            "predicted_churn_rate": get_churn_rate(),
            "average_churn_probability": (
                get_average_churn_probability()
            ),
        },

        "risk_distribution": get_risk_distribution(),
        "risk_segment_summary": get_risk_segment_summary(),
        "customer_metrics_by_risk": get_customer_metrics_by_risk(),
        "top_risk_factors": get_top_risk_factors(),
        "risk_factors_by_risk_level": get_risk_factors_by_risk_level()
    }