from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_chroma import Chroma


DOCUMENT_DIR = Path(__file__).parent / "documents"

VECTOR_DB_DIR = Path(__file__).parent / "chroma_db"


def load_documents():

    documents = []

    for file_path in DOCUMENT_DIR.iterdir():

        if file_path.suffix.lower() == ".pdf":

            loader = PyPDFLoader(
                str(file_path)
            )

            documents.extend(
                loader.load()
            )

        elif file_path.suffix.lower() == ".md":

            loader = TextLoader(
                str(file_path),
                encoding="utf-8"
            )

            documents.extend(
                loader.load()
            )

    return documents


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    return splitter.split_documents(
        documents
    )


def create_vector_store(chunks):

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR)
    )

    return vector_store


if __name__ == "__main__":

    documents = load_documents()
    print(f"Loaded {len(documents)} document pages.")

    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    vector_store = create_vector_store(chunks)
    print("Vector database created successfully.")