from pathlib import Path

import joblib
import mlflow


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MLFLOW_DB_PATH = PROJECT_ROOT / "mlflow.db"
MODEL_PATH = PROJECT_ROOT / "models" / "churn_model.pkl"

MODEL_NAME = "CustomerChurn_RF"
MODEL_VERSION = "1"

mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB_PATH}")

print(f"MLflow tracking URI: sqlite:///{MLFLOW_DB_PATH}")
print(f"Loading model: {MODEL_NAME} version {MODEL_VERSION}")

model = mlflow.sklearn.load_model(
    f"models:/{MODEL_NAME}/{MODEL_VERSION}"
)

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(model, MODEL_PATH)

print(f"Model exported successfully: {MODEL_PATH}")
print(f"Model type: {type(model)}")