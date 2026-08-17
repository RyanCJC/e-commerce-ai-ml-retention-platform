from rag.query_builder import build_retention_query
from rag.retriever import retrieve_retention_knowledge


def retrieve_customer_retention_knowledge(
    customer_data: dict,
    churn_probability: float,
    risk_level: str,
    feature_contributions: list[dict],
    strategy_focus: str,
    k: int = 4
):

    query = build_retention_query(
        customer_data=customer_data,
        churn_probability=churn_probability,
        risk_level=risk_level,
        feature_contributions=feature_contributions,
        strategy_focus=strategy_focus
    )

    documents = retrieve_retention_knowledge(
        query=query,
        k=k
    )

    return documents
