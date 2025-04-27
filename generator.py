# generator.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AnswerGenerator:
    def __init__(self, model="gpt-4o"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate_answer(self, query, retrieved_docs):
        # Merge all retrieved documents into one context
        combined_context = "\n\n".join(retrieved_docs)

        prompt = f"""
        Anda adalah asisten hukum yang bertugas membantu menjawab pertanyaan user berdasarkan dokumen hukum yang diberikan.

        Aturan main Anda:
        - Bacalah dengan cermat semua informasi yang tersedia di dalam dokumen hukum (UU PDP).
        - Prioritaskan menggunakan informasi dari dokumen terlebih dahulu untuk menjawab.
        - Jika istilah atau konsep yang ditanyakan tidak muncul persis sama, gunakan pemahaman dari istilah terkait di dokumen (misalnya: definisi, tujuan, kategori, hak, kewajiban).
        - Jika pertanyaan meminta nomor pasal tertentu, jawab dengan hanya menyebutkan nomor pasal yang relevan.
        - Jika pertanyaan menanyakan isi atau bunyi pasal, tuliskan isi pasal dengan nomor tersebut sesuai dokumen.
        - Jika dokumen sama sekali tidak mencakup jawaban, baru Anda boleh memberikan penjelasan umum berdasarkan konteks online.
        - **Namun, pastikan Anda selalu mengecek apakah konteks tambahan tersebut sesuai atau terkait dengan dokumen yang diberikan.**
        - Jika setelah semua pengecekan tidak ada relevansi, minta maaf bahwa jawaban tidak ditemukan berdasarkan dokumen.
        - Jika Anda membuat daftar item (seperti langkah, dokumen, atau syarat), gunakan penomoran atau tanda bullet (1., 2., 3. ...).

        ---
        📄 Informasi (Dokumen Hukum):
        {combined_context}

        ---
        ❓ Pertanyaan:
        {query}

        ---
        💬 Jawaban:
        """

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Anda adalah asisten hukum yang hanya boleh menjawab berdasarkan dokumen yang diberikan. Anda boleh merangkum jika diperlukan."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=700
        )

        return completion.choices[0].message.content
