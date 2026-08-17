import os
from dotenv import load_dotenv
from src.inference.predictor import predict_churn, explain_churn
from llm.schemas import RetentionRecommendation

from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class GraphState(TypedDict):
    message: str
    customer_data: dict
    churn_prediction: int | None
    churn_probability: float | None
    risk_level: str | None
    feature_contributions: list[dict] | None
    response: RetentionRecommendation | None


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    # temperature=0   # Deprecated for Gemini 3.x models
)

structured_llm = llm.with_structured_output(
    RetentionRecommendation
)


def predict_customer_churn(state: GraphState):

    result = predict_churn(state["customer_data"])

    return {
        "churn_prediction": result["churn_prediction"],
        "churn_probability": result["churn_probability"],
        "risk_level": result["risk_level"]
    }

def explain_prediction(state: GraphState):

    explanations = explain_churn(state["customer_data"])

    return {
        "feature_contributions": explanations
    }

def route_by_risk(state: GraphState):

    risk_level = state["risk_level"]

    if risk_level == "High":
        return "high_risk"

    elif risk_level == "Medium":
        return "medium_risk"

    else:
        return "low_risk"



def high_risk_recommendation(state: GraphState):

    prompt = f"""
        You are a customer retention specialist handling a HIGH-RISK customer.

        Analyze the customer using ONLY the information provided.

        Customer data:
        {state["customer_data"]}

        Machine learning result:
        - Churn prediction: {state["churn_prediction"]}
        - Churn probability: {state["churn_probability"]:.4f}
        - Risk level: {state["risk_level"]}

        SHAP model explanation:
        {state["feature_contributions"]}

        User request:
        {state["message"]}

        Your task:

        1. Explain why the model identifies this customer as high risk.
        2. Identify the most important model-attributed risk factors.
        3. Recommend practical and prioritized retention actions.
        4. Focus on proactive intervention because this customer has high
        predicted churn risk.

        Important rules:

        - Treat the ML prediction as the source of truth.
        - Do not change or override the ML prediction.
        - SHAP values represent model attribution, not causation.
        - Do not claim that a feature caused churn.
        - Do not invent customer behavior, complaints, or interactions.
        - Base your explanation on the supplied customer data and model output.
        """

    response = structured_llm.invoke(prompt)

    return {
        "response": response
    }


def medium_risk_recommendation(state: GraphState):

    prompt = f"""
        You are a customer retention specialist handling a MEDIUM-RISK customer.

        Analyze the customer using ONLY the information provided.

        Customer data:
        {state["customer_data"]}

        Machine learning result:
        - Churn prediction: {state["churn_prediction"]}
        - Churn probability: {state["churn_probability"]:.4f}
        - Risk level: {state["risk_level"]}

        SHAP model explanation:
        {state["feature_contributions"]}

        User request:
        {state["message"]}

        Your task:

        1. Explain the customer's moderate churn risk.
        2. Identify the most important factors influencing the model prediction.
        3. Recommend preventive retention actions.
        4. Focus on increasing engagement and addressing potential weaknesses
        before the customer becomes high risk.

        Important rules:

        - Treat the ML prediction as the source of truth.
        - Do not change or override the ML prediction.
        - SHAP values represent model attribution, not causation.
        - Do not claim that a feature caused churn.
        - Do not invent customer behavior, complaints, or interactions.
        - Base your explanation on the supplied customer data and model output.
        """

    response = structured_llm.invoke(prompt)

    return {
        "response": response
    }

def low_risk_recommendation(state: GraphState):

    prompt = f"""
        You are a customer retention specialist handling a LOW-RISK customer.

        Analyze the customer using ONLY the information provided.

        Customer data:
        {state["customer_data"]}

        Machine learning result:
        - Churn prediction: {state["churn_prediction"]}
        - Churn probability: {state["churn_probability"]:.4f}
        - Risk level: {state["risk_level"]}

        SHAP model explanation:
        {state["feature_contributions"]}

        User request:
        {state["message"]}

        Your task:

        1. Explain why the customer currently appears to have low churn risk.
        2. Identify the most relevant model-attributed factors.
        3. Recommend lightweight engagement or loyalty actions.
        4. Avoid unnecessarily aggressive retention interventions.

        Important rules:

        - Treat the ML prediction as the source of truth.
        - Do not change or override the ML prediction.
        - SHAP values represent model attribution, not causation.
        - Do not claim that a feature caused churn.
        - Do not invent customer behavior, complaints, or interactions.
        - Base your explanation on the supplied customer data and model output.
        """

    response = structured_llm.invoke(prompt)

    return {
        "response": response
    }



graph_builder = StateGraph(GraphState)

graph_builder.add_node(
    "predict_customer_churn",
    predict_customer_churn
)

graph_builder.add_node(
    "explain_prediction",
    explain_prediction
)

graph_builder.add_node(
    "high_risk_recommendation",
    high_risk_recommendation
)

graph_builder.add_node(
    "medium_risk_recommendation",
    medium_risk_recommendation
)

graph_builder.add_node(
    "low_risk_recommendation",
    low_risk_recommendation
)


graph_builder.add_edge(
    START,
    "predict_customer_churn"
)

graph_builder.add_edge(
    "predict_customer_churn",
    "explain_prediction"
)

graph_builder.add_conditional_edges(
    "explain_prediction",
    route_by_risk,
    {
        "high_risk": "high_risk_recommendation",
        "medium_risk": "medium_risk_recommendation",
        "low_risk": "low_risk_recommendation"
    }
)

graph_builder.add_edge(
    "high_risk_recommendation",
    END
)

graph_builder.add_edge(
    "medium_risk_recommendation",
    END
)

graph_builder.add_edge(
    "low_risk_recommendation",
    END
)

graph = graph_builder.compile()

# png_bytes = graph.get_graph().draw_mermaid_png()

# with open("langgraph_workflow.png", "wb") as f:
#     f.write(png_bytes)

def analyze_customer(
    customer_data: dict,
    message: str
) -> dict:

    result = graph.invoke(
        {
            "message": message,
            "customer_data": customer_data,
            "churn_prediction": None,
            "churn_probability": None,
            "risk_level": None,
            "feature_contributions": None,
            "response": None
        }
    )

    return {
        "churn_prediction": result["churn_prediction"],
        "churn_probability": result["churn_probability"],
        "risk_level": result["risk_level"],
        "feature_contributions": result["feature_contributions"],
        "recommendation": result["response"]
    }