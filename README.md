# Custom NER Model Project

## Student
**Name:** Thanseera S  
**Branch/Year:** CSE (AI & ML), III Year

## Project Description
This project is a custom Named Entity Recognition (NER) model using **spaCy**. It extracts entities like **COMPANY**, **ORG**, **SECTOR**, and others from text data. The project includes data annotation, model training, testing, and evaluation.

## Files in the Repository
- `annotations.json` → Annotated dataset used for training.  
- `finance_data.txt` → Raw text used for testing and demonstration.  
- `base_config.cfg` → spaCy configuration file used for training the model.  
- `train.spacy` and `dev.spacy` → Preprocessed training and validation datasets (optional).  
- `test_model.py` → Python script to test the trained model on any text input.  
- `NER_PROJECT.ipynb` → Notebook showing full workflow: data annotation, training, testing, and evaluation.

## How to Run
1. **Install spaCy** if not already installed:
   ```bash
   pip install spacy
   ```
2. **Test the model** using the Python script:
   ```bash
   python test_model.py
   ```
3. **Optional:** Open the notebook `NER_PROJECT.ipynb` to see detailed steps including data annotation, model training, testing, and evaluation.

## Download Links
You can download the trained models from Google Drive:

- **Model Best:** [Download model-best](https://drive.google.com/drive/folders/1P0pyUBaoq5OUzlmeaTO612vHgCUnP2ES?usp=sharing)
- **Model Last:**[Download model-last](https://drive.google.com/drive/folders/1GHb4RNVJFW-2Z38OZgEEpQq1Kawc_P5O?usp=drive_link)

## Notes
- `model-best` contains the best-performing model from training.  
- `model-last` is the last checkpoint from training.  

## Project Workflow
1. Annotate data using `annotations.json`.  
2. Convert annotations to `train.spacy` and `dev.spacy`.  
3. Configure and train the NER model using `base_config.cfg`.  
4. Evaluate model performance on the dev set.  
5. Test the trained model on new text samples using `test_model.py`.  
6. Optional: Deploy or integrate the model into applications.
