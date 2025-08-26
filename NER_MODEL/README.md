### NER Training with spaCy

This repo contains two Colab notebooks for training a Named Entity Recognition (NER) model on Finance data.

## Notebooks

CPU + No Transformer → Trains spaCy’s ner pipeline (lighter, faster, works without GPU).

GPU + Transformer → Uses Hugging Face transformer with spaCy for higher accuracy (requires GPU runtime).

## Labels Used

NOTE: Annotation can be done using the open source tool https://arunmozhi.in/ner-annotator/

STOCK

REVENUE

MARKET_CAP

EARNINGS

DIVIDEND

EVENT

MERGER

## Usage

Open Colab.

Upload the two JSON files in either notebooks depending upon:

1. Run CPU notebook if you don’t need transformer/GPU.

2. Run GPU notebook (set runtime → GPU) for transformer-based accuracy.


