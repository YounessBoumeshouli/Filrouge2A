import json
import time
import mlflow
from sentence_transformers import SentenceTransformer
import chromadb
import os

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("RAG_Indexing")

start_time = time.time()

with mlflow.start_run(run_name="embedding_ingestion"):

    text_chunks_path = os.path.join(
        os.path.dirname(__file__), "../../data/text_chunks.json"
    )
    table_chunks_path = os.path.join(
        os.path.dirname(__file__), "../../data/table_chunks.json"
    )
    DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/chroma_db")

    with open(text_chunks_path, "r", encoding="utf-8") as f:
        text_chunks = json.load(f)

    with open(table_chunks_path, "r", encoding="utf-8") as f:
        table_chunks = json.load(f)

    COLLECTION_NAME = "medical_chunks"

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
    model = SentenceTransformer(EMBEDDING_MODEL)

    mlflow.log_param("embedding_model", EMBEDDING_MODEL)
    mlflow.log_param("chroma_db_path", DB_PATH)
    mlflow.log_param("collection_name", COLLECTION_NAME)

    mlflow.log_param("num_text_chunks", len(text_chunks))
    mlflow.log_param("num_table_chunks", len(table_chunks))

    total_indexed = 0
    embedding_dim = None

    for i, chunk in enumerate(text_chunks):
        embedding = model.encode(chunk["content"])

        if embedding_dim is None:
            embedding_dim = len(embedding)

        collection.add(
            ids=[f"text_{i}"],
            metadatas=[
                {
                    "title": chunk["title"],
                    "page": chunk["page"],
                    "domain": chunk.get("domain", ""),
                }
            ],
            documents=[chunk["content"]],
            embeddings=[embedding.tolist()],
        )

        total_indexed += 1

    for i, table in enumerate(table_chunks):
        row_data = table.get("row", {})
        full_text = " ".join([f"{k}: {v}" for k, v in row_data.items()])

        embedding = model.encode(full_text)

        collection.add(
            ids=[f"table_{i}"],
            metadatas=[{"table_id": table.get("table_id"), "type": "table"}],
            documents=[json.dumps(row_data, ensure_ascii=False)],
            embeddings=[embedding.tolist()],
        )

        total_indexed += 1

    duration = time.time() - start_time

    mlflow.log_metric("total_chunks_indexed", total_indexed)
    mlflow.log_metric("embedding_dimension", embedding_dim if embedding_dim else 0)
    mlflow.log_metric("indexing_duration_seconds", duration)

print("All chunks embedded and stored in ChromaDB ")
