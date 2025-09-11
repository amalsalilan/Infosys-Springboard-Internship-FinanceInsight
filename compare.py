from transformers import pipeline
import spacy
from prettytable import PrettyTable
import torch

device = 0 if torch.cuda.is_available() else -1   

ner_pipeline = pipeline(
    "ner",
    model="Jean-Baptiste/roberta-large-ner-english",
    grouped_entities=True,
    device=device
)

nlp = spacy.load("en_core_web_trf") 
text = """
Apple Inc reported a revenue of $20 billion in Q2 2023.
Goldman Sachs invested $500 million in Tesla.
The Reserve Bank of India announced a rate hike of 0.25% in March 2023.
"""

bert_entities = ner_pipeline(text)
bert_dict = {ent['word'].strip(): ent['entity_group'] for ent in bert_entities}
doc = nlp(text)
spacy_dict = {ent.text.strip(): ent.label_ for ent in doc.ents}

def normalize_entity(ent):
    return ent.lower().replace("the ", "").strip()

bert_norm = {normalize_entity(k): v for k, v in bert_dict.items()}
spacy_norm = {normalize_entity(k): v for k, v in spacy_dict.items()}

all_entities = set(bert_norm.keys()).union(set(spacy_norm.keys()))

table = PrettyTable()
table.field_names = ["Entity", "RoBERTa-Large (HF)", "spaCy", "Match?"]

for ent in all_entities:
    bert_label = bert_norm.get(ent, "-")
    spacy_label = spacy_norm.get(ent, "-")
    match = "✅" if bert_label == spacy_label and bert_label != "-" else "❌"
    table.add_row([ent, bert_label, spacy_label, match])

print("Comparison of NER Outputs: RoBERTa-Large (Hugging Face) vs spaCy\n")
print(table)
