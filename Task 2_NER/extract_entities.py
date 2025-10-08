# NER extraction from pdf
# Written by Yogeshwar Prabhu

import pdfplumber
import spacy
import json
from spacy import displacy

# load spacy model
# note: trf is slow, sm is fallback
try:
    nlp = spacy.load("en_core_web_trf")
except:
    print("could not load trf model, using sm")
    nlp = spacy.load("en_core_web_sm")

pdf_file = "minutes.pdf"   # pdf file name
all_text = ""

# open pdf and read text
with pdfplumber.open(pdf_file) as pdf:
    for p in pdf.pages:
        t = p.extract_text()
        if t:
            all_text += t + "\n"

# run NER
doc = nlp(all_text)

# save entities in jsonl
with open("entities.jsonl", "w", encoding="utf-8") as f:
    for ent in doc.ents:
        rec = {
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char
        }
        f.write(json.dumps(rec) + "\n")

print("entities saved in entities.jsonl")

# displacy visualization
html = displacy.render(doc, style="ent")
with open("displacy_output.html", "w", encoding="utf-8") as f:
    f.write(html)

print("saved displacy_output.html")