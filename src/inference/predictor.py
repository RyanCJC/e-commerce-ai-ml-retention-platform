import mlflow
import mlflow.sklearn
import pandas as pd
from pathlib import Path
import shap

# PROJECT PATH
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MLFLOW_DB_PATH = PROJECT_ROOT / "mlflow.db"

# MLFLOW CONFIGURATION
mlflow.set_tracking_uri(
    f"sqlite:///{MLFLOW_DB_PATH}"
)

# LOAD REGISTERED MODEL
MODEL_NAME = "CustomerChurn_RF"
MODEL_VERSION = "1"

MODEL_URI = f"models:/{MODEL_NAME}/{MODEL_VERSION}"

model = mlflow.sklearn.load_model(
    MODEL_URI
)

# PIPELINE COMPONENTS
preprocessor = model.named_steps["preprocessor"]
rf_model = model.named_steps["model"]

# SHAP EXPLAINER
explainer = shap.TreeExplainer(
    rf_model
)

# RISK LEVEL
def get_risk_level(probability: float) -> str:

    if probability >= 0.70:
        return "High"

    if probability >= 0.40:
        return "Medium"

    return "Low"

# CHURN PREDICTION
def predict_churn(customer_data: dict) -> dict:

    input_df = pd.DataFrame([customer_data])

    # Model prediction
    prediction = model.predict(input_df)[0]

    # Churn probability
    probability = model.predict_proba(input_df)[0, 1]
    probability = float(probability)

    # Risk level
    risk_level = get_risk_level(probability)

    return {
        "churn_prediction": int(prediction),
        "churn_probability": probability,
        "risk_level": risk_level
    }


# CHURN EXPLANATION
def explain_churn(customer_data: dict) -> list[dict]:

    input_df = pd.DataFrame([customer_data])

    # Transform input using the same preprocessing
    # used by the trained model
    X_transformed = preprocessor.transform(input_df)

    # Get transformed feature names
    feature_names = preprocessor.get_feature_names_out()

    # Calculate SHAP values
    shap_explanation = explainer(X_transformed)

    # First sample, all features, churn class
    shap_values = shap_explanation.values[0, :, 1]

    # Create feature contribution table
    shap_df = pd.DataFrame({
        "feature": feature_names,
        "shap_value": shap_values
    })

    # Absolute contribution
    shap_df["absolute_shap"] = (
        shap_df["shap_value"].abs()
    )

    # Most important features first
    shap_df = shap_df.sort_values(
        "absolute_shap",
        ascending=False
    )

    # Select Top 5
    top_features = shap_df.head(5)

    feature_contributions = []

    for _, row in top_features.iterrows():

        direction = (
            "increases churn risk"
            if row["shap_value"] > 0
            else "decreases churn risk"
        )

        feature_contributions.append({
            "feature": row["feature"],
            "shap_value": float(row["shap_value"]),
            "direction": direction
        })

    return feature_contributions