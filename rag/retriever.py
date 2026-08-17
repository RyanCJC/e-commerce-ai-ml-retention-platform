from pathlib import Path

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_chroma import Chroma


VECTOR_DB_DIR = Path(__file__).parent / "chroma_db"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vector_store = Chroma(
    persist_directory=str(VECTOR_DB_DIR),
    embedding_function=embeddings
)


def retrieve_retention_knowledge(
    query: str,
    k: int = 4
):
    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


if __name__ == "__main__":

    query = """
    Customer retention strategies for an e-commerce customer
    with moderate churn risk, low purchase frequency,
    and relatively low customer satisfaction.
    Focus on increasing repeat purchases and customer engagement.
    """

    results = retrieve_retention_knowledge(
        query,
        k=4
    )

    for i, result in enumerate(results, start=1):

        print("\n====================")
        print(f"RESULT {i}")
        print("====================")

        print(result.page_content)

        print("\nMetadata:")
        print(result.metadata)