#!/usr/bin/env python3
"""
Script to regenerate RAG embeddings with new Marrakech places data
"""

# import os
import sys
import json
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def regenerate_embeddings():
    """Regenerate embeddings with new Marrakech data"""
    try:
        # Import after path setup
        from app.rag.retriever_simple import model, client

        logger.info("🗑️ Clearing existing embeddings...")

        # Clear existing collection
        try:
            client.delete_collection("medical_chunks")
            logger.info("✓ Deleted old collection")
        except Exception as e:
            logger.info(f"Collection didn't exist or couldn't delete: {e}")

        # Create new collection
        collection = client.get_or_create_collection(name="medical_chunks")
        logger.info("✓ Created new collection")

        # Load new Marrakech data
        data_file = backend_dir / "app" / "data" / "text_chunks.json"
        logger.info(f"📖 Loading data from {data_file}")

        with open(data_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        logger.info(f"✓ Loaded {len(chunks)} chunks")

        # Generate embeddings and add to collection
        logger.info("🔄 Generating embeddings...")

        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            documents.append(chunk["content"])
            metadatas.append(
                {
                    "source": chunk["metadata"]["source"],
                    "chunk_index": chunk["metadata"]["chunk_index"],
                }
            )
            ids.append(chunk["chunk_id"])

        # Generate embeddings using the model
        logger.info("🧠 Computing embeddings with sentence-transformers...")
        embeddings = model.encode(documents)

        # Add to ChromaDB
        logger.info("💾 Adding to ChromaDB...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings.tolist(),
        )

        logger.info(f"✅ Successfully added {len(documents)} documents to ChromaDB")

        # Test the new embeddings
        logger.info("🧪 Testing new embeddings...")
        test_query = "Tell me about Jemaa el-Fna"
        test_results = collection.query(query_texts=[test_query], n_results=3)

        logger.info(f"Test query: '{test_query}'")
        logger.info(f"Found {len(test_results['documents'][0])} results:")
        for i, doc in enumerate(test_results["documents"][0][:2]):
            logger.info(f"  {i+1}. {doc[:100]}...")

        logger.info("🎉 Embeddings regeneration complete!")
        return True

    except Exception as e:
        logger.error(f"❌ Error regenerating embeddings: {e}")
        return False


def main():
    print("=== RAG Embeddings Regeneration ===")
    print("Replacing medical data with Marrakech places data")
    print()

    success = regenerate_embeddings()

    if success:
        print("\n✅ SUCCESS: RAG system updated with Marrakech places data!")
        print("The chatbot will now provide information about:")
        print("- Jemaa el-Fna and main attractions")
        print("- All major souks and their specialties")
        print("- Palaces, gardens, and monuments")
        print("- Practical travel tips and prices")
        print("- Food, accommodation, and cultural info")
        print("\nYou can now test the RAG API with Marrakech-related queries!")
    else:
        print("\n❌ FAILED: Could not regenerate embeddings")
        print("Check the error messages above for details")


if __name__ == "__main__":
    main()
