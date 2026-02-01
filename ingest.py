import os
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings import HuggingFaceEmbeddings # <--- Changement ici
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# 1. Chargement des clés
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Nom de la collection
COLLECTION_NAME = "network_grok_v1"

# 2. Chargement du CSV
print("📂 Lecture du fichier network.csv...")
try:
    df = pd.read_csv("network.csv")
    # Petit nettoyage si jamais il y a des espaces dans les noms de colonnes
    df.columns = df.columns.str.strip()
    print(f"   -> {len(df)} lignes trouvées.")
except Exception as e:
    print(f"❌ Erreur de lecture CSV : {e}")
    exit()

# Création du texte à vectoriser
df['text'] = df.apply(lambda row: f"Log Machine: {row.to_json()}", axis=1)

# 3. Vectorisation (Mode HuggingFace - Plus stable)
print("⚙️ Téléchargement du modèle IA (HuggingFace)...")
# Ce modèle est le standard mondial. Il va se télécharger au 1er lancement.
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

loader = DataFrameLoader(df, page_content_column="text")
documents = loader.load()

# 4. Envoi vers Qdrant
print(f"🚀 Envoi vers Qdrant (Collection: {COLLECTION_NAME})...")
print("   Cela peut prendre quelques minutes pour 10k lignes. Patientez...")

try:
    qdrant = QdrantVectorStore.from_documents(
        documents,
        embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        force_recreate=True
    )
    print("✅ SUCCÈS TOTAL ! Votre dataset complet est dans Qdrant.")
except Exception as e:
    print(f"❌ Erreur lors de l'envoi Qdrant : {e}")

