📜 UUPDP RAG Chatbot
A Retrieval-Augmented Generation (RAG) chatbot built with FastAPI, OpenAI, and ChromaDB.

This chatbot can answer questions about the Undang-Undang Pelindungan Data Pribadi (UU PDP) by retrieving the most relevant legal documents and generating natural language responses.

🚀 Features
🔍 Semantic Search over UU PDP law chunks

➕ Query Augmentation for enhanced legal context

🔄 Multi-Step Retrieval Fallback for robust performance

🖋️ Markdown to HTML Rendering for clean web output

⚡ FastAPI Backend with HTML frontend

🗄️ Optional Local Storage with ChromaDB

📂 Project Structure

├── app.py                  # FastAPI web server  
├── retriever.py            # Retrieval logic from ChromaDB  
├── generator.py            # OpenAI answer generation  
├── ingest_data.py          # Data embedding and database population  
├── templates/  
│   └── index.html          # Frontend web page  
├── data/  
│   └── UUPDP_with_embeddings.parquet  
├── db/                     # ChromaDB database files  
├── static/                 # (Optional) CSS/JS files  
└── requirements.txt        # Python dependencies  

🛠️ Installation
1. Clone the Repository
git clone https://github.com/your-username/uupdp-rag-chatbot.git
cd uupdp-rag-chatbot

2. Install Python Dependencies
pip install -r requirements.txt

3. Set Up Environment Variables
Create a .env file in the project root and add your OpenAI API key:
OPENAI_API_KEY=your-openai-api-key

4. Ingest the Data
Run the following script to populate the database with embedded legal documents:
python ingest_data.py

🚀 Running the App
Start the FastAPI server with:
uvicorn app:app --reload

Then, open your browser and visit:
http://127.0.0.1:8000
