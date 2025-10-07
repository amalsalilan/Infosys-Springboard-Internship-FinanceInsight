# Financial Named Entity Recognition (NER) 

This repository contains both the **frontend** and **backend** of a **Financial Named Entity Recognition (NER)** system.

The project identifies **financial entities** such as company names, monetary amounts, and domain-specific terms using a fine-tuned **BERT model**, combined with **SpaCy** and **LangDetect**.

---

## ⚠️ Note

Due to **GitHub’s 100 MB file size limit**, the **trained model files** (`.safetensors`, `.bin`, etc.) are **not uploaded here**.  
The full prject is stored separately and can be downloaded from Google Drive.

👉 [Download working model Files (Google Drive)](https://drive.google.com/file/d/1B_Zc4cSfwQUp9kCMy-Uz5E49CcDKnSPT/view?usp=drive_link)


---

## 📁 Folder Structure

```

financial-ner/
│
├── backend/                  # Python backend (FastAPI)
│   ├── app.py                # Main API server
│   ├── requirements.txt      # Backend dependencies
│   ├── SPACY_MODEL
|   ├── BERT_MODEL/      
│   ├── config.cfg            # Model configs (weights not uploaded)
│   ├── meta.json
│
├── frontend/                 # TypeScript + React + Vite frontend
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│
├── README.md
└── ...

````

> 💡 Both **frontend** and **backend** are inside this same repository.

---

## ⚙️ Installation & Setup

### 🧠 Backend Setup 

1️⃣ Navigate to the backend folder:
```bash
cd backend
````

2️⃣ Install all required dependencies (no virtual environment needed):

```bash
pip install -r requirements.txt
```

3️⃣ Run the backend server:

```bash
python app.py
```

> Backend runs at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### 🌐 Frontend Setup (Vite + React + TypeScript)

1️⃣ Navigate to the frontend folder:

```bash
cd frontend
```

2️⃣ Install dependencies:

```bash
npm install
```

3️⃣ Start the frontend development server:

```bash
npm run dev
```

> Frontend runs at **[http://localhost:5173](http://localhost:5173)**

---

## 🧰 Technologies Used

Backend: Python (FastAPI)

Frontend: TypeScript, React, Vite

Styling: Tailwind CSS

models : BERT - Sentiment Classification ;
         Lang- Data Extraction ;
         SpaCy-Entity Recognition ;


---

## ⚙️ Example Output Summary

### 📄 Extracted Text

```
This Agreement is entered into on the 5th day of July, 2024...
```

---

### 🟢 SpaCy Entities

Alpha Technologies Pvt. Ltd. → ORG

July 5, 2024 → DATE

USD 125,000 → MONEY

---

### 🔵 BERT Sentiment

✅ **Positive tone**
Confidence: **0.89**

---

### 🟣 LangExtract Table

| Field            | Value                        |
| ---------------- | ---------------------------- |
| agreement_date   | July 5, 2024                 |
| service_provider | Alpha Technologies Pvt. Ltd. |
| client           | Delta Innovations Inc.       |
| contract_value   | USD 125,000                  |
| jurisdiction     | California                   |


---

## 🖼️ Output Preview

<img width="1897" height="982" alt="image" src="https://github.com/user-attachments/assets/5f4f804b-5ece-4945-879e-e10b6be9630a" />
<img width="625" height="343" alt="image" src="https://github.com/user-attachments/assets/d96200a4-85b2-43cb-aeb0-03fbca1edb8a" />
<img width="546" height="672" alt="image" src="https://github.com/user-attachments/assets/cc61b177-b020-4f3d-99a1-2c1c2d081977" />
<img width="535" height="747" alt="image" src="https://github.com/user-attachments/assets/b259fd75-c16b-46da-b1c2-cf6a4303a8c5" />

---


Then open your browser → **[http://localhost:5173](http://localhost:5173)**

---

---

##  Acknowledgements

* [Hugging Face Transformers](https://huggingface.co/transformers)
* [SpaCy](https://spacy.io)
* [LangDetect](https://pypi.org/project/langdetect/)
* [FastAPI](https://fastapi.tiangolo.com/) / [Flask](https://flask.palletsprojects.com/)
* [Vite](https://vitejs.dev/)
* [Tailwind CSS](https://tailwindcss.com/)

```
