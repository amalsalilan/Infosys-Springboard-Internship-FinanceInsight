import pdfplumber 
import spacy
from spacy import displacy
import json

# Load the small English model (instead of en_core_web_trf)
nlp = spacy.load("en_core_web_md")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                lines = page_text.split('\n')
                for line in lines:
                    if line.strip():
                        if line.strip().istitle() and not text.endswith("\n"):
                            text += f"\n{line}\n"
                        else:
                            text += f"{line} "
                text += "\n"
    return text.strip()

# Path to your PDF
pdf_path = "Alpha Technologies Pvt. Ltd.pdf"  
contract_text = extract_text_from_pdf(pdf_path)

# Run NER
doc = nlp(contract_text)

# Customize visualization colors
displacy_options = {"colors": {"ORG": "#7aecec", "DATE": "#bfeeb7", "GPE": "#feca74"}}
html = displacy.render(doc, style="ent", options=displacy_options, jupyter=False)

# Save visualization as HTML
with open("entities_visualization.html", "w", encoding="utf-8") as f:
    f.write(html)

# Save extracted entities in JSONL format
with open("entities.jsonl", "w", encoding="utf-8") as f:
    for ent in doc.ents:
        entity_dict = {
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char
        }
        f.write(json.dumps(entity_dict) + "\n")

# Print first 5 extracted entities
print("\n✅ Extracted Entities (sample):")
for ent in doc.ents[:5]:
    print({"text": ent.text, "label": ent.label_})
