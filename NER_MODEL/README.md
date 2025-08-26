### Custom NER Model
## Overview

This project trains a custom Named Entity Recognition (NER) model using spaCy. The model is trained on a small annotated dataset to recognize entities like Persons, Organizations, Locations, Titles/Occupations, and Landmarks.

## Files

1. ner_training_text.txt -> Training text 

2. training_data.json -> Json file containing the annotated version of ner_training_text.txt. NOTE: Annotation is done using the open source tool: https://arunmozhi.in/ner-annotator/

3. NER.ipynb -> Notebook to train the model and evaluate it.

4. config.cfg -> Contains the necessary information (required for training) like:
   1. CPU/GPU for training.
   2. Which spacy model is being used.
   3. Optimize for efficiency or accuracy etc.
   NOTE: config file can be generated with the help of command or by using the site: https://spacy.io/        

5. training_data.spacy: Generated docBin object required for actually training the model.

## ENTITIES RECOGNIZED

1. PERSON: Name of a person
2. ORG: Any organization
3. LOC: A specific place in a city/country.
4. OCC: Occupation
5. GPE: City/Country
6. DATE: Day, month, year.


