from pathlib import Path

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_chroma import Chroma


VECTOR_DB_DIR = (
    Path(__file__).parent / "chroma_db"
)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vector_store = Chroma(
    persist_directory=str(VECTOR_DB_DIR),
    embedding_function=embeddings
)


retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 4
    }
)

def retrieve_retention_knowledge(
    query: str
):

    documents = retriever.invoke(
        query
    )

    return documents