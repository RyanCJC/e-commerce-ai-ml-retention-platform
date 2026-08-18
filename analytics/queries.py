import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def get_top_risk_factors(limit: int = 10):

    result = (
        supabase
        .table("churn_analyses")
        .select("feature_contributions")
        .execute()
    )

    feature_scores = {}

    for row in result.data:

        contributions = row.get("feature_contributions")

        if not contributions:
            continue

        for contribution in contributions:

            feature = contribution.get("feature")
            shap_value = contribution.get("shap_value")

            if feature is None or shap_value is None:
                continue

            if feature not in feature_scores:
                feature_scores[feature] = {
                    "feature": feature,
                    "total_abs_shap": 0.0,
                    "positive_count": 0,
                    "negative_count": 0
                }

            feature_scores[feature]["total_abs_shap"] += abs(
                float(shap_value)
            )

            if float(shap_value) > 0:
                feature_scores[feature]["positive_count"] += 1

            elif float(shap_value) < 0:
                feature_scores[feature]["negative_count"] += 1

    results = list(feature_scores.values())

    results.sort(
        key=lambda x: x["total_abs_shap"],
        reverse=True
    )

    return results[:limit]


def get_total_customers():

    result = (
        supabase
        .table("customers")
        .select("id", count="exact")
        .execute()
    )

    return result.count or 0


def get_churn_rate():

    result = (
        supabase
        .table("churn_analyses")
        .select("churn_prediction")
        .execute()
    )

    analyses = result.data

    if not analyses:
        return 0.0

    churned = sum(
        1
        for row in analyses
        if row["churn_prediction"] == 1
    )

    return churned / len(analyses)


def get_risk_distribution():

    result = (
        supabase
        .table("churn_analyses")
        .select("risk_level")
        .execute()
    )

    distribution = {
        "Low": 0,
        "Medium": 0,
        "High": 0
    }

    for row in result.data:

        risk = row["risk_level"]

        if risk in distribution:
            distribution[risk] += 1

    return distribution


def get_average_churn_probability():

    result = (
        supabase
        .table("churn_analyses")
        .select("churn_probability")
        .execute()
    )

    probabilities = [
        float(row["churn_probability"])
        for row in result.data
    ]

    if not probabilities:
        return 0.0

    return sum(probabilities) / len(probabilities)


def get_risk_segment_summary():

    analyses = (
        supabase
        .table("churn_analyses")
        .select(
            "customer_id, risk_level, churn_probability"
        )
        .execute()
    ).data

    customers = (
        supabase
        .table("customers")
        .select(
            "id, frequency, monetary, avg_order_value, "
            "avg_review_score, late_delivery_ratio"
        )
        .execute()
    ).data

    customer_lookup = {
        customer["id"]: customer
        for customer in customers
    }

    summary = {}

    for analysis in analyses:

        customer = customer_lookup.get(
            analysis["customer_id"]
        )

        if not customer:
            continue

        risk = analysis["risk_level"]

        if risk not in summary:
            summary[risk] = {
                "customer_count": 0,
                "total_probability": 0,
                "total_frequency": 0,
                "total_monetary": 0,
                "total_review_score": 0,
                "total_late_delivery_ratio": 0
            }

        summary[risk]["customer_count"] += 1
        summary[risk]["total_probability"] += float(
            analysis["churn_probability"]
        )
        summary[risk]["total_frequency"] += customer["frequency"]
        summary[risk]["total_monetary"] += customer["monetary"]
        summary[risk]["total_review_score"] += customer["avg_review_score"]
        summary[risk]["total_late_delivery_ratio"] += customer["late_delivery_ratio"]

    for risk, values in summary.items():

        count = values["customer_count"]

        values["avg_churn_probability"] = (
            values["total_probability"] / count
        )

        values["avg_frequency"] = (
            values["total_frequency"] / count
        )

        values["avg_monetary"] = (
            values["total_monetary"] / count
        )

        values["avg_review_score"] = (
            values["total_review_score"] / count
        )

        values["avg_late_delivery_ratio"] = (
            values["total_late_delivery_ratio"] / count
        )

        del values["total_probability"]
        del values["total_frequency"]
        del values["total_monetary"]
        del values["total_review_score"]
        del values["total_late_delivery_ratio"]

    return summary



def get_customer_metrics_by_risk():

    analyses = (
        supabase
        .table("churn_analyses")
        .select(
            "customer_id, risk_level"
        )
        .execute()
    ).data

    customers = (
        supabase
        .table("customers")
        .select(
            "id, frequency, monetary, avg_order_value, "
            "unique_categories, unique_sellers, avg_review_score, "
            "late_delivery_ratio, avg_installments"
        )
        .execute()
    ).data

    customer_lookup = {
        customer["id"]: customer
        for customer in customers
    }

    metrics = {
        "Low": [],
        "Medium": [],
        "High": []
    }

    for analysis in analyses:

        customer = customer_lookup.get(
            analysis["customer_id"]
        )

        if not customer:
            continue

        risk = analysis["risk_level"]

        if risk not in metrics:
            continue

        metrics[risk].append(customer)

    result = {}

    for risk, customers_list in metrics.items():

        if not customers_list:
            result[risk] = {
                "customer_count": 0
            }
            continue

        count = len(customers_list)

        result[risk] = {
            "customer_count": count,

            "avg_frequency": (
                sum(
                    float(c["frequency"])
                    for c in customers_list
                ) / count
            ),

            "avg_monetary": (
                sum(
                    float(c["monetary"])
                    for c in customers_list
                ) / count
            ),

            "avg_order_value": (
                sum(
                    float(c["avg_order_value"])
                    for c in customers_list
                ) / count
            ),

            "avg_unique_categories": (
                sum(
                    float(c["unique_categories"])
                    for c in customers_list
                ) / count
            ),

            "avg_unique_sellers": (
                sum(
                    float(c["unique_sellers"])
                    for c in customers_list
                ) / count
            ),

            "avg_review_score": (
                sum(
                    float(c["avg_review_score"])
                    for c in customers_list
                ) / count
            ),

            "avg_late_delivery_ratio": (
                sum(
                    float(c["late_delivery_ratio"])
                    for c in customers_list
                ) / count
            ),

            "avg_installments": (
                sum(
                    float(c["avg_installments"])
                    for c in customers_list
                ) / count
            )
        }

    return result


def get_risk_factors_by_risk_level(limit: int = 5):

    analyses = (
        supabase
        .table("churn_analyses")
        .select(
            "risk_level, feature_contributions"
        )
        .execute()
    ).data

    feature_scores = {
        "Low": {},
        "Medium": {},
        "High": {}
    }

    for analysis in analyses:

        risk = analysis["risk_level"]

        if risk not in feature_scores:
            continue

        contributions = analysis.get(
            "feature_contributions"
        )

        if not contributions:
            continue

        for contribution in contributions:

            feature = contribution.get("feature")
            shap_value = contribution.get("shap_value")

            if feature is None or shap_value is None:
                continue

            shap_value = float(shap_value)

            if feature not in feature_scores[risk]:

                feature_scores[risk][feature] = {
                    "feature": feature,
                    "total_abs_shap": 0.0,
                    "positive_count": 0,
                    "negative_count": 0
                }

            feature_scores[risk][feature][
                "total_abs_shap"
            ] += abs(shap_value)

            if shap_value > 0:

                feature_scores[risk][feature][
                    "positive_count"
                ] += 1

            elif shap_value < 0:

                feature_scores[risk][feature][
                    "negative_count"
                ] += 1

    result = {}

    for risk, features in feature_scores.items():

        factors = list(features.values())

        factors.sort(
            key=lambda x: x["total_abs_shap"],
            reverse=True
        )

        result[risk] = factors[:limit]

    return result