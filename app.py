# app.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from retriever import ChromaRetriever
from generator import AnswerGenerator

import re
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

retriever = ChromaRetriever()
generator = AnswerGenerator()

def augment_query(original_query: str) -> str:
    """Add UU PDP context to the query."""
    context_prefix = "Dalam konteks Undang-Undang Pelindungan Data Pribadi (UU PDP), "
    return context_prefix + original_query.strip()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "question": "", "answer": "", "sources": []})

@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, question: str = Form(...)):
    augmented_question = augment_query(question)
    docs, metas = retriever.retrieve(augmented_question)
    
    if docs:
        answer = generator.generate_answer(augmented_question, docs)
    else:
        answer = "Maaf, saya tidak menemukan jawaban berdasarkan dokumen ini."

    # 🧩 Group and Sort Sources
    sources = []

    def extract_pasal_number(pasal_str):
        match = re.search(r'Pasal\s*(\d+)', pasal_str)
        if match:
            return int(match.group(1))
        else:
            return 9999

    def clean_pasal_display(pasal_str):
        return re.sub(r'\s*\(Part\s*\d+\)', '', pasal_str).strip()

    grouped_sources = defaultdict(list)

    for meta in metas:
        bab = meta.get('bab', 'Bab Tidak Diketahui')
        pasal_number = meta.get('pasal_number', '')
        grouped_sources[bab].append(pasal_number)

    for bab in sorted(grouped_sources.keys()):
        sorted_pasals = sorted(grouped_sources[bab], key=extract_pasal_number)
        displayed_pasals = set()

        for pasal in sorted_pasals:
            clean_pasal = clean_pasal_display(pasal)
            if clean_pasal not in displayed_pasals:
                sources.append({
                    "bab": bab,
                    "pasal_number": clean_pasal
                })
                displayed_pasals.add(clean_pasal)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "question": question,
        "answer": answer,
        "sources": sources
    })
