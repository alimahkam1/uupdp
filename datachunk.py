import docx
import re
import pandas as pd

def load_docx_paragraphs(docx_path):
    """Load paragraphs from DOCX."""
    doc = docx.Document(docx_path)
    return [para.text.strip() for para in doc.paragraphs if para.text.strip()]

def clean_text(text):
    """Clean spaces and newlines."""
    return re.sub(r'\s+', ' ', text).strip()

def split_long_text(text, max_length=1000):
    """Split long text into smaller chunks."""
    sentences = re.split(r'(?<=[.;])\s+', text)
    parts = []
    current = ''

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_length:
            current += ' ' + sentence
        else:
            if current:
                parts.append(current.strip())
            current = sentence

    if current:
        parts.append(current.strip())

    return parts

def parse_penjelasan(paragraphs):
    """Parse Penjelasan section."""
    penjelasan_dict = {}
    start = False
    current_pasal = None

    for para in paragraphs:
        if 'PENJELASAN ATAS UNDANG-UNDANG' in para:
            start = True
            continue

        if start:
            match = re.match(r'^Pasal\s+(\d+)', para)
            if match:
                current_pasal = f"Pasal {match.group(1)}"
                penjelasan_dict[current_pasal] = []
            elif 'Cukup jelas' in para and current_pasal:
                penjelasan_dict[current_pasal].append('Cukup jelas.')
            elif current_pasal:
                penjelasan_dict[current_pasal].append(para)

    for pasal in penjelasan_dict:
        penjelasan_dict[pasal] = ' '.join(penjelasan_dict[pasal]).strip()

    return penjelasan_dict

def process_docx(docx_path, output_csv_path):
    paragraphs = load_docx_paragraphs(docx_path)

    main_paragraphs = []
    penjelasan_paragraphs = []
    is_penjelasan = False
    found_bab = False

    for para in paragraphs:
        if 'PENJELASAN ATAS UNDANG-UNDANG' in para:
            is_penjelasan = True
        if is_penjelasan:
            penjelasan_paragraphs.append(para)
        else:
            if re.match(r'^BAB\s+[IVXLCDM]+$', para.strip()):
                found_bab = True
            if found_bab:
                main_paragraphs.append(para)

    # Parsing BABs and Pasals
    chunks = []
    current_bab = None
    current_pasal = None
    buffer = []
    bab_title_pending = False

    for para in main_paragraphs:
        # Detect BAB
        if re.match(r'^BAB\s+[IVXLCDM]+$', para.strip()):
            # 🚨 Save existing Pasal before switching BAB
            if current_pasal and buffer:
                chunks.append({
                    'bab': current_bab,
                    'pasal_number': current_pasal,
                    'text': clean_text(' '.join(buffer))
                })
                buffer = []
                current_pasal = None

            current_bab = para.strip()
            bab_title_pending = True
            continue

        if bab_title_pending:
            current_bab += ' ' + para.strip()
            bab_title_pending = False
            continue

        # Detect Pasal
        if re.match(r'^Pasal\s+\d+', para):
            if current_pasal and buffer:
                chunks.append({
                    'bab': current_bab,
                    'pasal_number': current_pasal,
                    'text': clean_text(' '.join(buffer))
                })
                buffer = []
            current_pasal = para.strip()

        # Normal paragraph text
        elif current_pasal:
            buffer.append(para)

    # After loop ends, save the last Pasal
    if current_pasal and buffer:
        chunks.append({
            'bab': current_bab,
            'pasal_number': current_pasal,
            'text': clean_text(' '.join(buffer))
        })

    # Parse Penjelasan
    penjelasan_mapping = parse_penjelasan(penjelasan_paragraphs)

    # Prepare final output with splitting
    final_chunks = []

    for chunk in chunks:
        bab = chunk['bab']
        pasal_number = chunk['pasal_number']
        text = chunk['text']
        penjelasan = penjelasan_mapping.get(pasal_number, '')

        if len(text) > 1000:
            parts = split_long_text(text)
            for idx, part in enumerate(parts):
                final_chunks.append({
                    'bab': bab,
                    'pasal_number': f"{pasal_number} (Part {idx+1})",
                    'text': part,
                    'penjelasan': penjelasan
                })
        else:
            final_chunks.append({
                'bab': bab,
                'pasal_number': pasal_number,
                'text': text,
                'penjelasan': penjelasan
            })

    df = pd.DataFrame(final_chunks)
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ CSV generated at: {output_csv_path}")
    print(f"Total {len(df)} rows extracted.")

# Example Usage
docx_path = 'data/UUPDP.docx'              # Your DOCX file path
output_csv_path = 'data/UUPDP_cleaned.csv'  # Output CSV path
process_docx(docx_path, output_csv_path)
