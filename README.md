# Financial Named Entity Recognition (NER) – Full Stack Project

This repository contains both the **frontend** and **backend** of a full-stack **Financial Named Entity Recognition (NER)** system.

The project identifies **financial entities** such as company names, monetary amounts, and domain-specific terms using a fine-tuned **BERT model**, combined with **SpaCy** and **LangDetect**.

---

## ⚠️ Note

Due to **GitHub’s 100 MB file size limit**, the **trained model files** (`.safetensors`, `.bin`, etc.) are **not uploaded here**.  
They are stored separately and can be downloaded from Google Drive.

👉 [Download Model Files (Google Drive)](https://drive.google.com/file/d/1B_Zc4cSfwQUp9kCMy-Uz5E49CcDKnSPT/view?usp=drive_link)

After downloading, place them inside:
```

backend/FINAL_NER_MODEL/
├── bert_model/
│   ├── model.safetensors
│   ├── training_args.bin
├── financial_bert_model/
│   ├── model.safetensors

```

---

## 📁 Folder Structure

```

financial-ner/
│
├── backend/                  # Python backend (FastAPI / Flask)
│   ├── app.py                # Main API server
│   ├── requirements.txt      # Backend dependencies
│   ├── FINAL_NER_MODEL/      # Model configs (weights not uploaded)
│   ├── config.cfg
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

### 🧠 Backend Setup (FastAPI / Flask)

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

Backend: Python (FastAPI / Flask)

Frontend: TypeScript, React, Vite

Styling: Tailwind CSS

models : BERT - Sentiment Classification
         Lang- Data Extraction
         SpaCy-Entity Recognition


---

## 🖼️ Output Preview



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
