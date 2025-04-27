 # app.py

from retriever import ChromaRetriever
from generator import AnswerGenerator
import re
from collections import defaultdict

def main():
    retriever = ChromaRetriever()
    generator = AnswerGenerator()

    while True:
        query = input("\nTanya apa saja tentang UUPDP (ketik 'exit' untuk keluar): ")
        if query.lower() == 'exit':
            break

        docs, metas = retriever.retrieve(query)
        
        if not docs:
            print("\nMaaf, saya tidak menemukan jawaban yang relevan.")
            continue

        #print("\n📄 Pasal Context Preview:")
        #for doc in docs:
        #    print(doc)
        print("\n🔍 Now generating answer...")

        answer = generator.generate_answer(query, docs)

        print("\nJawaban:")
        print(answer)

        # # Optional: Show source info
        # print("\n(Sumber terkait)")
        # for meta in metas:
        #     print(f"Bab: {meta.get('bab')}, Pasal: {meta.get('pasal_number')}")
        
        print("\n(Sumber terkait)")

        def extract_pasal_number(pasal_str):
            match = re.search(r'Pasal\s*(\d+)', pasal_str)
            if match:
                return int(match.group(1))
            else:
                return 9999  # Unknown or messy pasal

        def clean_pasal_display(pasal_str):
            """Remove (Part X) from pasal display."""
            return re.sub(r'\s*\(Part\s*\d+\)', '', pasal_str).strip()

        # 1. Group sources by Bab
        grouped_sources = defaultdict(list)

        for meta in metas:
            bab = meta.get('bab', 'Bab Tidak Diketahui')
            pasal_number = meta.get('pasal_number', '')
            grouped_sources[bab].append(pasal_number)

        # 2. Sort and display cleanly
        for bab in sorted(grouped_sources.keys()):
            print(f"📚 {bab}")
            
            # Sort Pasal numbers
            sorted_pasals = sorted(grouped_sources[bab], key=extract_pasal_number)
            
            displayed_pasals = set()  # Avoid duplicate display

            for pasal in sorted_pasals:
                clean_pasal = clean_pasal_display(pasal)

                # Only show each Pasal once, even if it had multiple parts
                if clean_pasal not in displayed_pasals:
                    print(f"    📜 {clean_pasal}")
                    displayed_pasals.add(clean_pasal)


if __name__ == "__main__":
    main()
