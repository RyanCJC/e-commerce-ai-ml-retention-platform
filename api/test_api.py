import requests


BASE_URL = "http://127.0.0.1:8000"


def test_health():
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_prediction():
    payload = {
        "frequency": 2,
        "monetary": 82.82,
        "avg_order_value": 41.41,
        "unique_categories": 2,
        "unique_sellers": 2,
        "avg_review_score": 4.5,
        "late_delivery_ratio": 0.0,
        "avg_installments": 1.0,
        "max_installments": 1.0,
        "payment_method_count": 1,
        "preferred_payment_type": "credit_card",
        "state": "SP",
        "latitude": -23.577482,
        "longitude": -46.587077
    }

    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["churn_prediction"] in [0, 1]
    assert 0 <= data["churn_probability"] <= 1