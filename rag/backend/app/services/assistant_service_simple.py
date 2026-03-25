import ollama
import os
import logging
import time
from app.rag.retriever_simple import hybrid_search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

LLM_CONFIG = {
    "model": "gemma2:2b",
    "temperature": 0.0,
    "top_p": 0.9,
    "top_k": 40,
    "num_predict": 2000,
    "timeout": 600
}

RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay": 2,
    "backoff_factor": 2
}

SYSTEM_PROMPT = """
Tu es CliniQ, Tu dois répondre UNIQUEMENT avec les informations du CONTEXTE ci-dessous.

RÈGLES ABSOLUES:
1. COPIE INTÉGRALEMENT toutes les informations pertinentes du CONTEXTE
2. NE RÉSUME PAS - donne TOUTES les informations disponibles
3. NE JAMAIS ajouter d'informations qui ne sont pas dans le contexte
4. NE JAMAIS utiliser tes connaissances générales
5. Si plusieurs informations sont pertinentes, LISTE-LES TOUTES sans exception
6. Si l'information n'est PAS dans le contexte: "Cette information n'est pas disponible dans ma documentation."

CONTEXTE (5 documents trouvés - utilise TOUS ceux qui sont pertinents):
{context}

Question: {question}
La réponse doit être rédigée sous forme de texte fluide et naturel, comme si elle venait d'un assistant intelligent.

Commence toujours par :
"Bonjour 👋, voici ce que j'ai trouvé pour vous :"

Ensuite :

Reformule les informations du contexte de manière claire et structurée.

Utilise un ton professionnel et amical.

Intègre naturellement les informations au lieu de faire une simple liste brute.

Ensuite, rédige uniquement les informations disponibles dans le contexte, en copiant ou reformulant strictement ce qui est écrit.

⚠️ Ne jamais ajouter d'exemples, de causes possibles, ni de recommandations personnelles."""

def check_ollama_health() -> bool:
    """Vérifie si Ollama est accessible"""
    try:
        client = ollama.Client(host=OLLAMA_HOST, timeout=5)
        client.list()
        return True
    except Exception as e:
        logger.warning(f"⚠️ Ollama non accessible: {str(e)}")
        return False

def pull_model_if_needed(model_name: str) -> bool:
    """Télécharge le modèle si nécessaire"""
    try:
        client = ollama.Client(host=OLLAMA_HOST, timeout=30)
        models = client.list()
        model_exists = any(model_name in m.get('name', '') for m in models.get('models', []))
        
        if not model_exists:
            logger.info(f"📥 Téléchargement du modèle {model_name}...")
            client.pull(model_name)
            logger.info(f"✓ Modèle {model_name} téléchargé")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement modèle: {str(e)}")
        return False

def generate_with_retry(client, model, messages, options, max_retries=3):
    """Génère une réponse avec retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Tentative {attempt + 1}/{max_retries}")
            response = client.chat(model=model, messages=messages, options=options)
            return response
        except Exception as e:
            error_msg = str(e).lower()
            if "timed out" in error_msg or "timeout" in error_msg:
                if attempt < max_retries - 1:
                    delay = RETRY_CONFIG["initial_delay"] * (RETRY_CONFIG["backoff_factor"] ** attempt)
                    logger.warning(f"⏳ Timeout - nouvelle tentative dans {delay}s...")
                    time.sleep(delay)
                    continue
            raise
    raise Exception(f"Échec après {max_retries} tentatives")

def generate_simple(question: str, k: int = 5) -> str:
    """Simplified generate function without complex dependencies"""
    try:
        if not check_ollama_health():
            raise Exception("❌ Ollama n'est pas accessible. Vérifiez qu'Ollama est démarré sur votre machine.")
        
        print(f"\n🔍 Recherche de documents pour: {question[:50]}...")
        logger.info(f"🔍 Recherche de documents pour: {question[:50]}...")
        
        chunks = hybrid_search(question, k) or []
        
        print(f"✓ {len(chunks)} documents trouvés")
        logger.info(f"✓ {len(chunks)} documents trouvés")
        
        if chunks:
            print("📄 Aperçu des documents:")
            logger.info("📄 Aperçu des documents:")
            for i, chunk in enumerate(chunks[:3], 1):
                preview = chunk.get('content', '')[:80]
                print(f"  Doc {i}: {preview}...")
                logger.info(f"  Doc {i}: {preview}...")
        
        retrieval_context = [c.get("content", "") for c in chunks]
        context = "\n\n---\n\n".join(retrieval_context)
        print(f"📝 Contexte total: {len(context)} caractères")
        logger.info(f"📝 Contexte total: {len(context)} caractères")

        print(f"\n🤖 Génération de la réponse avec {LLM_CONFIG['model']}...")
        logger.info(f"🤖 Génération de la réponse avec {LLM_CONFIG['model']}...")
        
        client = ollama.Client(host=OLLAMA_HOST, timeout=LLM_CONFIG["timeout"])
        full_prompt = SYSTEM_PROMPT.format(context=context, question=question)
        
        print(f"📋 Prompt total: {len(full_prompt)} caractères")
        logger.info(f"📋 Prompt total: {len(full_prompt)} caractères")

        print("🚀 Envoi de la requête au modèle...")
        logger.info("🚀 Envoi de la requête au modèle...")
        
        response = generate_with_retry(
            client=client,
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "system", "content": "Tu es un assistant clinique strict basé sur RAG."},
                {"role": "user", "content": full_prompt}
            ],
            options={
                "temperature": LLM_CONFIG["temperature"],
                "top_p": LLM_CONFIG["top_p"],
                "top_k": LLM_CONFIG["top_k"],
                "num_predict": LLM_CONFIG["num_predict"]
            },
            max_retries=RETRY_CONFIG["max_retries"]
        )

        print("📥 Réponse reçue du modèle")
        logger.info("📥 Réponse reçue du modèle")
        
        answer = response["message"]["content"].replace("\n", " ")
        
        print(f"✓ Réponse générée avec succès ({len(answer)} caractères)")
        logger.info(f"✓ Réponse générée avec succès ({len(answer)} caractères)")
        
        print(f"💬 Aperçu: {answer[:100]}...\n")
        logger.info(f"💬 Aperçu: {answer[:100]}...")
        
        return answer
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erreur: {error_msg}")
        logger.error(f"❌ Erreur: {error_msg}")
        
        if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            raise Exception(
                "⏱️ Le modèle prend trop de temps à répondre. "
                "Vérifiez: 1) Ollama est démarré, 2) Le modèle gemma2:2b est téléchargé (ollama pull gemma2:2b), "
                "3) Votre machine a assez de ressources (RAM/CPU)."
            )
        raise Exception(f"Erreur génération: {error_msg}")

# Alias for compatibility
generate = generate_simple