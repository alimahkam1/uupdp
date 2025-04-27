# embed_data.py

import os
import pandas as pd
import openai
import numpy as np
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text, model="text-embedding-3-small"):
    """Call OpenAI to get embedding of text."""
    try:
        response = openai.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

# Load your cleaned input file (ONLY text + metadata columns)
print("🔎 Loading cleaned data...")
df = pd.read_csv('data/UUPDP_cleaned.csv')

# Fill empty texts if any
df['text'] = df['text'].fillna('')

# Prepare to collect embeddings
embeddings = []
print(f"🚀 Starting embedding generation for {len(df)} texts...")

for idx, row in df.iterrows():
    text = row['text']
    emb = get_embedding(text)
    if emb is not None:
        embeddings.append(emb)
    else:
        # fallback: empty embedding
        embeddings.append([0]*1536)  # ✅ Correct fallback dimension

    # Optional: short sleep to avoid rate limit
    time.sleep(0.2)

# Create a DataFrame from embeddings
print("📦 Converting embeddings to DataFrame...")
embedding_df = pd.DataFrame(embeddings)

# ✅ Carefully select only desired metadata columns
metadata_df = df[['bab', 'pasal_number', 'text', 'penjelasan']]

# ✅ Concatenate metadata + embeddings cleanly
final_df = pd.concat([metadata_df, embedding_df], axis=1)

# Save to CSV
final_df.to_csv('data/UUPDP_with_embeddings.csv', index=False, encoding='utf-8-sig')

# Save to Parquet
final_df.to_parquet('data/UUPDP_with_embeddings.parquet', index=False)

print("🎉✅ Embeddings done and saved to both CSV and Parquet!")
