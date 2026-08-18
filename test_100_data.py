import random
import requests
import time


API_URL = "http://127.0.0.1:8000/analyze"

NUM_CUSTOMERS = 100


def generate_customer():

    frequency = random.randint(1, 10)

    monetary = round(
        random.uniform(30, 1000),
        2
    )

    avg_order_value = round(
        monetary / frequency,
        2
    )

    unique_categories = random.randint(
        1,
        min(frequency, 8)
    )

    unique_sellers = random.randint(
        1,
        min(frequency, 8)
    )

    avg_review_score = round(
        random.uniform(1.0, 5.0),
        1
    )

    late_delivery_ratio = round(
        random.uniform(0.0, 1.0),
        2
    )

    avg_installments = round(
        random.uniform(0.0, 6.0),
        1
    )

    max_installments = max(
        int(avg_installments),
        random.randint(0, 12)
    )

    payment_method_count = random.randint(
        1,
        4
    )

    payment_types = [
        "credit_card",
        "boleto",
        "voucher",
        "debit_card"
    ]

    preferred_payment_type = random.choice(
        payment_types
    )

    states = [
        "SP",
        "RJ",
        "MG",
        "RS",
        "PR",
        "SC",
        "BA",
        "GO",
        "PE",
        "CE"
    ]

    state = random.choice(states)

    # Approximate geographic coordinates.
    # They are only being used as model input,
    # not as precise real-world customer locations.
    latitude = round(
        random.uniform(-33.0, 5.0),
        4
    )

    longitude = round(
        random.uniform(-73.0, -34.0),
        4
    )

    return {
        "frequency": frequency,
        "monetary": monetary,
        "avg_order_value": avg_order_value,
        "unique_categories": unique_categories,
        "unique_sellers": unique_sellers,
        "avg_review_score": avg_review_score,
        "late_delivery_ratio": late_delivery_ratio,
        "avg_installments": avg_installments,
        "max_installments": max_installments,
        "payment_method_count": payment_method_count,
        "preferred_payment_type": preferred_payment_type,
        "state": state,
        "latitude": latitude,
        "longitude": longitude
    }


def main():

    successful = 0
    failed = 0

    print(
        f"Starting analysis for "
        f"{NUM_CUSTOMERS} customers...\n"
    )

    for i in range(1, NUM_CUSTOMERS + 1):

        customer = generate_customer()

        try:

            response = requests.post(
                API_URL,
                json=customer,
                timeout=120
            )

            if response.status_code == 200:

                result = response.json()

                successful += 1

                print(
                    f"[{i:03d}/{NUM_CUSTOMERS}] "
                    f"SUCCESS | "
                    f"Risk: {result['risk_level']} | "
                    f"Probability: "
                    f"{result['churn_probability']:.4f}"
                )

            else:

                failed += 1

                print(
                    f"[{i:03d}/{NUM_CUSTOMERS}] "
                    f"FAILED | "
                    f"HTTP {response.status_code}"
                )

                print(
                    response.text
                )

        except Exception as e:

            failed += 1

            print(
                f"[{i:03d}/{NUM_CUSTOMERS}] "
                f"ERROR | {e}"
            )

        # Small delay so that 100 requests don't hit
        # the API simultaneously.
        time.sleep(0.2)

    print("\n==============================")
    print("TEST COMPLETED")
    print("==============================")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Total:      {NUM_CUSTOMERS}")


if __name__ == "__main__":
    main()