from predictor import predict_churn


customer = {
    "frequency": 2,
    "monetary": 250.0,
    "avg_order_value": 125.0,
    "unique_categories": 2,
    "unique_sellers": 2,
    "avg_review_score": 3.5,
    "late_delivery_ratio": 0.3,
    "avg_installments": 2.0,
    "max_installments": 3.0,
    "payment_method_count": 1,
    "preferred_payment_type": "credit_card",
    "state": "SP",
    "latitude": -23.55,
    "longitude": -46.63
}


result = predict_churn(customer)

print("\nPrediction:")
print(result["churn_prediction"])

print("\nProbability:")
print(result["churn_probability"])

print("\nRisk:")
print(result["risk_level"])

print("\nFeature contributions:")

for feature in result["feature_contributions"]:
    print(feature)