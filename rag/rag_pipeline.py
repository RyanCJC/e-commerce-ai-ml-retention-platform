from rag.query_builder import build_retention_query
from rag.supabase_retriever import retrieve_retention_knowledge


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

    print("\n===== SUPABASE RAG RESULTS =====")

    for i, document in enumerate(documents, 1):
        print(f"\nResult {i}")
        print("Source:", document.metadata.get("source"))
        print("Page:", document.metadata.get("page"))
        print("Similarity:", document.metadata.get("similarity"))
        print(document.page_content[:300])

    return documents


# def format_rag_context(documents) -> str:

#     if not documents:
#         return "No relevant retention knowledge was retrieved."

#     return "\n\n".join(
#         document.page_content
#         for document in documents
#     )