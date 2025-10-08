import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
from pathlib import Path
import json

# --- Configuration ---
OUTPUT_DIR = Path("financial_spacy_model")
N_ITER = 30  # Training iterations

# --- Training Data (FIXED character indices) ---
TRAIN_DATA = [
    ("Sundar Pichai announced that Google earned $320 billion in California.", {
        "entities": [(0, 13, "PERSON"), (30, 36, "ORG"), (44, 56, "MONEY"), (60, 70, "GPE")]
    }),
    ("Elon Musk revealed that Tesla invested $5 billion in Texas.", {
        "entities": [(0, 9, "PERSON"), (24, 29, "ORG"), (39, 49, "MONEY"), (53, 58, "GPE")]
    }),
    ("Satya Nadella confirmed that Microsoft generated $250 billion in Washington.", {
        "entities": [(0, 13, "PERSON"), (29, 38, "ORG"), (49, 61, "MONEY"), (65, 75, "GPE")]
    }),
    ("Jeff Bezos donated $200 million to Amazon projects in India.", {
        "entities": [(0, 10, "PERSON"), (19, 31, "MONEY"), (35, 41, "ORG"), (54, 59, "GPE")]
    }),
    ("Mark Zuckerberg shared that Meta invested $12 billion in London.", {
        "entities": [(0, 15, "PERSON"), (28, 32, "ORG"), (42, 53, "MONEY"), (57, 63, "GPE")]
    }),
    ("Tim Cook reported that Apple reached $300 billion in Cupertino.", {
        "entities": [(0, 8, "PERSON"), (23, 28, "ORG"), (37, 49, "MONEY"), (53, 62, "GPE")]
    }),
    ("Bill Gates stated that Microsoft contributed $20 billion to New York.", {
        "entities": [(0, 10, "PERSON"), (23, 32, "ORG"), (45, 56, "MONEY"), (60, 68, "GPE")]
    }),
    ("Warren Buffett invests through Berkshire Hathaway in Omaha.", {
        "entities": [(0, 14, "PERSON"), (31, 49, "ORG"), (53, 58, "GPE")]
    }),
    ("Amazon announced new facilities in Seattle worth $500 million.", {
        "entities": [(0, 6, "ORG"), (35, 42, "GPE"), (49, 61, "MONEY")]
    }),
    ("Larry Page founded Google in California.", {
        "entities": [(0, 10, "PERSON"), (19, 25, "ORG"), (29, 39, "GPE")]
    }),
    ("Sergey Brin works at Google headquarters.", {
        "entities": [(0, 11, "PERSON"), (21, 27, "ORG")]
    }),
    ("Tesla manufactures vehicles in Austin.", {
        "entities": [(0, 5, "ORG"), (31, 37, "GPE")]
    }),
    ("Microsoft has offices in London and Paris.", {
        "entities": [(0, 9, "ORG"), (25, 31, "GPE"), (36, 41, "GPE")]
    }),
    ("Apple invested $2 billion in renewable energy.", {
        "entities": [(0, 5, "ORG"), (15, 25, "MONEY")]
    }),
    ("Narendra Modi announced that Infosys expanded in Bengaluru.", {
        "entities": [(0, 13, "PERSON"), (29, 36, "ORG"), (49, 58, "GPE")]
    }),
    ("SpaceX secured $2 billion in funding.", {
        "entities": [(0, 6, "ORG"), (15, 25, "MONEY")]
    }),
    ("Meta invested in infrastructure.", {
        "entities": [(0, 4, "ORG")]
    }),
    ("The headquarters are in Cupertino.", {
        "entities": [(24, 33, "GPE")]
    }),
    ("Infosys reported $50 million revenue.", {
        "entities": [(0, 7, "ORG"), (17, 28, "MONEY")]
    }),
    ("The company reported strong earnings.", {
        "entities": []
    }),
    ("Revenue growth exceeded expectations.", {
        "entities": []
    }),
    ("The investment was announced yesterday.", {
        "entities": []
    }),
    ("Profits increased in the quarter.", {
        "entities": []
    }),
    ("The board approved the plan.", {
        "entities": []
    }),
    ("Analysts predict continued growth.", {
        "entities": []
    }),
]

print("="*70)
print("SPACY NER TRAINING - PROGRAMMATIC APPROACH")
print("="*70)
print(f"\nTraining examples: {len(TRAIN_DATA)}")
print(f"Iterations: {N_ITER}\n")

# --- 1. Load base model ---
print("Loading base model 'en_core_web_sm'...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

print("✓ Base model loaded\n")

# --- 2. Add NER if not present, or get existing ---
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
    print("✓ Added NER component")
else:
    ner = nlp.get_pipe("ner")
    print("✓ Using existing NER component")

# --- 3. Add labels ---
print("\nAdding entity labels...")
labels = set()
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        labels.add(ent[2])

for label in labels:
    ner.add_label(label)
    print(f"  + {label}")

print(f"\n✓ Added {len(labels)} labels: {sorted(labels)}\n")

# --- 4. Training ---
print("="*70)
print("TRAINING")
print("="*70)

# Disable other pipes during training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    # Create optimizer
    optimizer = nlp.create_optimizer()
    
    # Training loop
    for iteration in range(N_ITER):
        random.shuffle(TRAIN_DATA)
        losses = {}
        
        # Create batches
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        
        for batch in batches:
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)
            
            # Update model
            nlp.update(examples, drop=0.35, sgd=optimizer, losses=losses)
        
        # Print progress every 5 iterations
        if (iteration + 1) % 5 == 0:
            print(f"Iteration {iteration + 1:>3}/{N_ITER} | Loss: {losses['ner']:>8.2f}")

print("\n✓ Training complete\n")

# --- 5. Save model ---
print("="*70)
print("SAVING MODEL")
print("="*70)

if OUTPUT_DIR.exists():
    import shutil
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
nlp.to_disk(OUTPUT_DIR)
print(f"✓ Model saved to: {OUTPUT_DIR}\n")

# --- 6. Test the model ---
print("="*70)
print("TESTING MODEL")
print("="*70)

# Reload the saved model
nlp_trained = spacy.load(OUTPUT_DIR)
print(f"✓ Model loaded from: {OUTPUT_DIR}\n")

TEST_CASES = [
    "Sundar Pichai announced that Google earned $320 billion in California.",
    "Elon Musk revealed that Tesla invested $5 billion in Texas.",
    "Jeff Bezos donated $200 million to Amazon projects in India.",
    "The company reported strong earnings this quarter.",
    "Microsoft operates in over 100 countries worldwide.",
    "Tim Cook visited Apple headquarters in Cupertino yesterday.",
    "Warren Buffett invested through Berkshire Hathaway.",
    "SpaceX secured $2 billion in funding from investors.",
]

entity_summary = {}

for i, text in enumerate(TEST_CASES, 1):
    doc = nlp_trained(text)
    print(f"Test {i}: {text}")
    
    if doc.ents:
        for ent in doc.ents:
            print(f"  ├─ {ent.label_:<8} → {ent.text}")
            entity_summary[ent.label_] = entity_summary.get(ent.label_, 0) + 1
    else:
        print(f"  └─ (no entities detected)")
    print()

# --- 7. Summary ---
print("="*70)
print("ENTITY SUMMARY")
print("="*70)

if entity_summary:
    total = sum(entity_summary.values())
    print(f"\nTotal entities detected: {total}\n")
    for label in sorted(entity_summary.keys()):
        count = entity_summary[label]
        percentage = (count / total) * 100
        print(f"  {label:<8} : {count:>3} ({percentage:>5.1f}%)")
else:
    print("\nNo entities detected in test cases.")

print("\n" + "="*70)
print("✓ COMPLETE!")
print("="*70)
print(f"\nModel location: {OUTPUT_DIR.absolute()}")
print("Load with: nlp = spacy.load('financial_spacy_model')")