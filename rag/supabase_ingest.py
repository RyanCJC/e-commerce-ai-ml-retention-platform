import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Configuration
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing from .env")


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "rag" / "documents"


# Supabase
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load PDFs
loader = PyPDFDirectoryLoader(
    str(DOCUMENTS_DIR)
)

documents = loader.load()

print(f"Loaded documents: {len(documents)}")


# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

chunks = text_splitter.split_documents(documents)

print(f"Created chunks: {len(chunks)}")


# Generate embeddings
texts = [
    chunk.page_content
    for chunk in chunks
]

vectors = embeddings.embed_documents(texts)

print(f"Generated embeddings: {len(vectors)}")
print(f"Embedding dimension: {len(vectors[0])}")


# Prepare database rows
rows = []

for chunk, vector in zip(chunks, vectors):

    metadata = chunk.metadata

    rows.append({
        "content": chunk.page_content,
        "embedding": vector,
        "source": metadata.get("source"),
        "page": metadata.get("page"),
        "metadata": metadata
    })


# Insert into Supabase
BATCH_SIZE = 50

for start in range(0, len(rows), BATCH_SIZE):

    batch = rows[start:start + BATCH_SIZE]

    supabase \
        .table("retention_knowledge") \
        .insert(batch) \
        .execute()

    print(
        f"Inserted {min(start + BATCH_SIZE, len(rows))}"
        f"/{len(rows)}"
    )


print("\n==============================")
print("INGESTION COMPLETE")
print("==============================")