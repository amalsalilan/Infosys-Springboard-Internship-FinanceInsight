FINANCE NER TRAINING

This project provides a Named Entity Recognition (NER) model designed for financial and business texts. The training is performed entirely on CPU, making it lightweight and accessible without requiring a GPU.

OBJECTIVE

Automatically extract important financial entities such as company names, monetary values, reporting dates, executives, products, and locations from financial reports, news articles, and related documents.

ENTITY LABELS USED

ORG – Company or institution names
DATE – Reporting periods, fiscal quarters, or years
PRODUCTS – Financial or tech products mentioned
LOCATION – Geographical references (countries, regions, markets)
AMT – Monetary amounts in different formats
PERSON – Names of executives or individuals quoted

WORKFLOW

ANNOTATION
Financial texts are annotated using NER Annotator. The annotated data is exported in spaCy JSON format.

TRAINING
The dataset is fed into spaCy’s standard NER pipeline (no transformer). Training runs efficiently on CPU and produces a model that can recognize financial entities.

EVALUATION
The model is tested against validation data to measure precision, recall, and F1-score.

USAGE

Once trained, the model can be used in financial analysis tools, contract parsing systems, or research projects.

EXAMPLE

Input Text:
Apple reported 25.3 billion U.S. dollars in Q1 2024, with Tim Cook emphasizing strong iPhone demand in Asia.

Extracted Entities:
ORG – Apple
AMT – 25.3 billion U.S. dollars
DATE – Q1 2024
PERSON – Tim Cook
PRODUCTS – iPhone
LOCATION – Asia

GETTING STARTED

Open the CPU training notebook in Colab.

Upload your annotated JSON dataset.

Run the notebook cells step by step.

Save the trained model for later use.

TOOLS

spaCy – for model training
Colab (CPU runtime) – for running the training
NER Annotator – for preparing labeled datasets
