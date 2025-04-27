# retriever.py

import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
import re

load_dotenv()

class ChromaRetriever:
    def __init__(self, persist_path="./db", collection_name="uupdp_law"):
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.openai_ef
        )

    def retrieve(self, query, n_results=15):
        # Step 1: Extract Pasal number from the query (if any)
        pasal_number = self.extract_pasal_number(query)

        filter_metadata = {}
        if pasal_number:
            filter_metadata = {
                "pasal_root": {"$eq": f"Pasal {pasal_number}"}
            }
            print(f"🔎 Using metadata filter: pasal_root = Pasal {pasal_number}")

        # Step 2: First attempt: metadata-filtered search
        print("🔍 Attempting retrieval with metadata filter...")
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata if filter_metadata else None
        )

        documents = results['documents'][0]
        metadatas = results['metadatas'][0]

        # Step 3: Check if fallback needed
        if not documents or all(doc.strip() == "" for doc in documents):
            print("⚠️ No good results. Fallback to pure semantic search (no filter)...")
            fallback_results = self.collection.query(
                query_texts=[query],
                n_results=n_results * 2  # Retrieve more chunks during fallback
            )
            documents = fallback_results['documents'][0]
            metadatas = fallback_results['metadatas'][0]

        # 🆕 ADD THIS DEBUG PRINT
        print("\n🧠 Retrieved documents:")
        for doc in documents:
            print(f"- {doc[:200]}...\n")  # Print first 200 chars for preview

        return documents, metadatas

    def extract_pasal_number(self, text):
        """Try to find a pasal number mentioned in the user query."""
        match = re.search(r'pasal\s*(\d+)', text.lower())
        if match:
            return match.group(1)
        return None
