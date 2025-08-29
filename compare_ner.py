import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import spacy
from prettytable import PrettyTable
import re

# Load BERT NER model
MODEL = "dslim/bert-base-NER"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForTokenClassification.from_pretrained(MODEL)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

# Sample text
text = "Apple Inc reported a revenue of $20 billion in Q2 2023. Goldman Sachs invested $500 million in Tesla. The Reserve Bank of India announced a rate hike of 0.25% in March 2023."

# --- Hugging Face BERT NER ---
print("\n--- Hugging Face BERT NER ---")
bert_results = ner_pipeline(text)
bert_entities = [(ent['word'], ent['entity_group']) for ent in bert_results]
for word, label in bert_entities:
    print(f"{word} -> {label}")

# --- spaCy NER ---
print("\n--- spaCy NER ---")
doc = nlp(text)
spacy_entities = [(ent.text, ent.label_) for ent in doc.ents]
for word, label in spacy_entities:
    print(f"{word} -> {label}")

# --- Comparison Table ---
print("\n--- Comparison Table (Cleaned) ---")

def normalize_entity(ent):
    """Normalize entity text: lowercase, remove leading 'the ', strip spaces."""
    ent = ent.lower().strip()
    ent = re.sub(r"^the\s+", "", ent)  # remove leading 'the'
    return ent

bert_dict = {normalize_entity(w): l for w, l in bert_entities}
spacy_dict = {normalize_entity(w): l for w, l in spacy_entities}

# Combine all unique entities
all_entities = set(list(bert_dict.keys()) + list(spacy_dict.keys()))

# Create PrettyTable
table = PrettyTable()
table.field_names = ["Entity", "BERT Label", "spaCy Label", "Match?"]

for ent in sorted(all_entities):
    bert_label = bert_dict.get(ent, "")
    spacy_label = spacy_dict.get(ent, "")
    match = "✅" if bert_label == spacy_label and bert_label != "" else "❌"
    table.add_row([ent, bert_label, spacy_label, match])

print(table)

# --- (Optional) Save output to file ---
with open("ner_output.txt", "w", encoding="utf-8") as f:
    f.write(str(table))
