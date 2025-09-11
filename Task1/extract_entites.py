import spacy

!python -m spacy download en_core_web_lg

nlp=spacy.load("en_core_web_lg")
nlp

import json

# Replace 'your_file.json' with your actual filename
with open('/content/annotations (1).json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# If it's a dict or list of texts, inspect it
print(data)

from spacy.tokens import DocBin

doc_bin = DocBin()

for text, ann in data["annotations"]:
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in ann["entities"]:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print(f"Skipping invalid span: {text[start:end]} ({label})")
        else:
            ents.append(span)
    doc.ents = ents
    doc_bin.add(doc)



doc_bin.to_disk("training_data.spacy")
print("Saved to training_data.spacy")

!python -m spacy init config config.cfg --lang en --pipeline ner

!python -m spacy train config.cfg --output ./output --paths.train ./training_data.spacy --paths.dev ./training_data.spacy

import spacy
from spacy import displacy

# Load your trained model directory
nlp = spacy.load("output/model-best")

text = """
On 15th August 2022, during the 75th Independence Day celebrations, Prime Minister Narendra Modi addressed the nation from the historic Red Fort in New Delhi.

In his speech, he highlighted the achievements of India in fields such as space technology, digital innovation, and renewable energy.

He mentioned successful projects like the Chandrayaan-2 mission launched by the Indian Space Research Organisation(ISRO) and the rise of fintech companies like Paytm and PhonePe.

Later that day, delegations from countries including the United States, Japan, and the United Arab Emirates (UAE) congratulated the government.

Reports from The Hindu and BBC News estimated that more than 50,000 people gathered near the fort to witness the celebrations, while over 200 million viewers watched it live on Doordarshan and YouTube.

In December 2021, the global technology giant Google LLC announced its plan to invest 1 billion USD in India’s digital ecosystem.

The investment was aimed at expanding access to cloud services and supporting small businesses across cities like Mumbai, Chennai, and Kolkata.

The announcement was made at the Google for India event, attended by Sundar Pichai, the CEO of Alphabet Inc., and Ashwini Vaishnaw, the Union Minister for Railways, Communications, and Electronics & Information Technology.

During the event, Google Cloud also revealed partnerships with companies like Reliance Jio, Bharti Airtel, and Wipro Technologies.

According to a report by Reuters, the deal is expected to create more than 10,000 jobs by 2024 and contribute significantly to the growth of Digital India initiatives.
"""

doc = nlp(text)

# This will display the highlighted entities directly in Jupyter notebook
displacy.render(doc, style="ent", jupyter=True)