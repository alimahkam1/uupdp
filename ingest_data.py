# ingest_data.py

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
import os
from dotenv import load_dotenv
import re
import shutil

# Load environment variables
load_dotenv()

# 1. Set up the correct embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# 2. Load your original data
print("🔎 Loading embedded data...")
df = pd.read_parquet('data/UUPDP_with_embeddings.parquet')

# 3. Check if embedding dimensions are correct (but we'll recompute embeddings later)
expected_embedding_dim = 1536
embedding_columns = df.columns[4:]  # Assuming first 4 columns are metadata

if len(embedding_columns) != expected_embedding_dim:
    raise ValueError(f"🚨 Embedding dimension mismatch! Expected {expected_embedding_dim}, found {len(embedding_columns)}.")

print(f"✅ Embedding dimension verified: {expected_embedding_dim}D.")

# 4. Generate pasal_root column
def extract_pasal_root(pasal_number):
    match = re.search(r"(Pasal\s*\d+)", pasal_number)
    if match:
        return match.group(1)
    return pasal_number  # fallback

print("🔨 Generating pasal_root column...")
df['pasal_root'] = df['pasal_number'].apply(extract_pasal_root)

# 5. Group by pasal_root to form full Pasal documents
print("🔨 Grouping documents by pasal_root...")
grouped_df = df.groupby('pasal_root').agg({
    'text': ' '.join,       # Combine all text fragments
    'bab': 'first',         # Take the first BAB
    'pasal_number': 'first', # Keep pasal number
    'penjelasan': 'first'   # Take first available penjelasan
}).reset_index()

df = grouped_df

# 6. Delete old ChromaDB if exists
if os.path.exists('./db'):
    print("🗑️  Removing old ChromaDB database...")
    shutil.rmtree('./db')

# 7. Initialize ChromaDB
print("🛜 Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="./db")

# 8. Create a new collection
collection_name = "uupdp_law"
collection = chroma_client.get_or_create_collection(
    name=collection_name,
    embedding_function=openai_ef
)

# 9. Prepare data
print("📦 Preparing documents, metadatas, and embeddings...")
documents = [
    f"{row['pasal_root']} - {row['pasal_number']}\n{row['text']}"
    for idx, row in df.iterrows()
]
metadatas = [
    {
        "bab": row['bab'],
        "pasal_number": row['pasal_number'],
        "pasal_root": row['pasal_root'],
        "penjelasan": row['penjelasan']
    }
    for idx, row in df.iterrows()
]
ids = [f"doc_{idx}" for idx in range(len(df))]

# 10. Generate embeddings for the full grouped pasal texts
print("🧠 Generating embeddings for full grouped pasal texts...")
embeddings = openai_ef(documents)

# 11. Add documents to ChromaDB
print("🚀 Adding documents to ChromaDB...")
collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)

print("🎉✅ Successfully populated ChromaDB with grouped full Pasal documents!")
