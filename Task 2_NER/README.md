# Task 2
# NER Task (Internship Work)

This task was about extracting Named Entities from a PDF of meeting notes.

---

### Folder Structure
```
NER-task/
├── extract_entities.py
├── requirements.txt
├── README.md
├── entities.jsonl
└── displacy_output.html
```

---

### What I did
- Read the pdf text using pdfplumber
- Applied spaCy NER model (`en_core_web_trf`, fallback to `en_core_web_sm`)
- Saved all entities in `entities.jsonl`
- Generated visualization using displaCy and saved it as html

---

### How to run
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_trf
python extract_entities.py
```
## Requirements
- **Python 3.8+**

- **Libraries**
  - `spacy` (v3.8 or later)
  - `pdfplumber`

- **Models**
  - `en_core_web_trf` (preferred, transformer-based model)
  - `en_core_web_sm` (fallback if transformer model crashes)

### Installation
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_trf
---

### Output files
- `entities.jsonl` → extracted entities list  
- `displacy_output.html` → open this file in a browser to see highlighted entities  

---

### Problems I faced
- Transformer model (trf) needs a lot of memory, so I used the small model (sm) when it crashed  
- PDF formatting was not always neat (line breaks made it tricky sometimes)  
- displaCy looks better inside Jupyter but I exported it as html for submission