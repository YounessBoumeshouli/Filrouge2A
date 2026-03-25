import chromadb
import json
from sentence_transformers import SentenceTransformer

DB_DIR = "app/data/chroma_db"
MODEL_NAME = "intfloat/multilingual-e5-base"

print("Chargement du modèle d'embedding...")
model = SentenceTransformer(MODEL_NAME)

print("Connexion à ChromaDB...")
client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(name="medical_chunks")

print(f"Nombre de documents dans la collection: {collection.count()}")

if collection.count() == 0:
    print("\nLa collection est vide. Chargement des données...")
    
    with open("app/data/text_chunks.json", "r", encoding="utf-8") as f:
        text_chunks = json.load(f)
    
    with open("app/data/table_chunks.json", "r", encoding="utf-8") as f:
        table_chunks = json.load(f)
    
    all_chunks = text_chunks + table_chunks
    print(f"Total de chunks à ajouter: {len(all_chunks)}")
    
    docs = []
    metas = []
    
    for c in all_chunks:
        if "content" in c:
            # Text chunk
            docs.append(c["content"])
            metas.append({k: v for k, v in c.items() if k != "content"})
        elif "row" in c:
            # Table chunk - convert row dict to string
            row_text = " | ".join([f"{k}: {v}" for k, v in c["row"].items()])
            docs.append(row_text)
            metas.append({"table_id": c.get("table_id", "unknown"), "type": "table"})
        else:
            print(f"Chunk ignoré: {c}")
    ids = [f"chunk_{i}" for i in range(len(all_chunks))]
    
    print("Génération des embeddings...")
    embeddings = model.encode(docs, show_progress_bar=True)
    
    print("Ajout à ChromaDB...")
    collection.add(
        documents=docs,
        metadatas=metas,
        ids=ids,
        embeddings=embeddings.tolist()
    )
    
    print(f"✓ {len(all_chunks)} documents ajoutés avec succès!")
else:
    print("✓ La base de données contient déjà des documents.")

print("\nTest de recherche...")
test_embedding = model.encode(["prurit traitement"])[0]
results = collection.query(
    query_embeddings=[test_embedding.tolist()],
    n_results=3
)
print(f"Résultats trouvés: {len(results['documents'][0])}")
for i, doc in enumerate(results['documents'][0]):
    print(f"\n{i+1}. {doc[:100]}...")
