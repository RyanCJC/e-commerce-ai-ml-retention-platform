import os

from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from rag.query_builder import build_retention_query

load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing from .env")


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def retrieve_retention_knowledge(
    query: str,
    k: int = 4
):

    query_embedding = embeddings.embed_query(query)

    result = supabase.rpc(
        "match_retention_knowledge",
        {
            "query_embedding": query_embedding,
            "match_count": k
        }
    ).execute()

    documents = []

    for row in result.data:

        document = Document(
            page_content=row["content"],
            metadata={
                "source": row["source"],
                "page": row["page"],
                "similarity": row["similarity"],
                **(row["metadata"] or {})
            }
        )

        documents.append(document)

    return documents


# if __name__ == "__main__":
    
#     customer_data = {
#         "frequency": 2,
#         "monetary": 250.0,
#         "avg_order_value": 125.0,
#         "unique_categories": 2,
#         "unique_sellers": 2,
#         "avg_review_score": 3.5,
#         "late_delivery_ratio": 0.3
#     }


#     feature_contributions = [
#         {
#             "feature": "numeric__avg_order_value",
#             "shap_value": 0.0173,
#             "direction": "increases churn risk"
#         },
#         {
#             "feature": "numeric__avg_review_score",
#             "shap_value": 0.0121,
#             "direction": "increases churn risk"
#         },
#         {
#             "feature": "categorical__state_SP",
#             "shap_value": -0.0561,
#             "direction": "decreases churn risk"
#         }
#     ]


#     query = build_retention_query(
#         customer_data=customer_data,
#         churn_probability=0.4002,
#         risk_level="Medium",
#         feature_contributions=feature_contributions
#     )


#     documents = retrieve_retention_knowledge(
#         query=query,
#         k=4
#     )


#     print("\n==============================")
#     print("SUPABASE RAG RESULTS")
#     print("==============================")


#     for i, document in enumerate(documents, start=1):

#         print(f"\n--- RESULT {i} ---")

#         print(document.page_content)

#         print("\nSimilarity:")
#         print(document.metadata["similarity"])