### NER Training with spaCy

This repo contains two Colab notebooks for training a Named Entity Recognition (NER) model on Finance/Contract data.

## Notebooks

CPU + No Transformer → Trains spaCy’s ner pipeline (lighter, faster, works without GPU).

GPU + Transformer → Uses Hugging Face transformer with spaCy for higher accuracy (requires GPU runtime).

## Labels Used

NOTE: Annotation can be done using the open source tool https://arunmozhi.in/ner-annotator/

ORG — Organization / Company name

GPE — Geo-political entity (city/state/country/address block)

DATE — Dates (day/month/year)

MONEY — Monetary amounts

DURATION — Contract duration (e.g., "12 months")

NOTICE — Termination notice period phrase

CONTRACT_REF — Contract/Reference number

ROLE — role string used in the contract context (e.g., "Service Provider")

MISC — other miscellaneous legal references (e.g., Companies Act citation)
## Usage

Open Colab.

Upload the two JSON files in either notebooks depending upon:

1. Run CPU notebook if you don’t need transformer/GPU.

2. Run GPU notebook (set runtime → GPU) for transformer-based accuracy.


