<<<<<<< HEAD
# FinSight - Financial Document Analysis

## Prerequisites

- Python 3.10+
- Node.js 16+
- Git
- uv (Python package manager)

## Setup

**1. Clone the repository:**
```bash
git clone https://github.com/amalsalilan/Infosys-Springboard-Internship-FinanceInsight.git
cd Infosys-Springboard-Internship-FinanceInsight
```

**2. Install uv (if not already installed):**
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**3. Install Python dependencies:**
```bash
uv sync

# On Windows, also install libmagic for langextract service:
uv pip install python-magic-bin
```

**4. Install Node dependencies:**
```bash
npm install
```

## Running the Application

**1. Start backend services:**
```bash
uv run python scripts/start_backend.py
```

**2. Start frontend (in a new terminal):**
```bash
npm run dev
```

**3. Access the application:**
Open your browser and navigate to `http://localhost:8080`
=======
# Finance NER Training

Welcome to the Finance NER Training project! This repository contains resources and instructions to build a Named Entity Recognition (NER) model tailored for financial and business texts. The training process is optimized for CPU environments, making it accessible for anyone with basic hardware.

---

## 🚀 Objective

Automatically extract important financial entities such as company names, monetary values, reporting dates, executives, products, and locations from financial reports, news articles, and related documents.

---

## 🏷️ Entity Labels

The model supports the following entity types:

- **ORG** – Company or institution names
- **DATE** – Reporting periods, fiscal quarters, or years
- **PRODUCTS** – Financial or tech products mentioned
- **LOCATION** – Geographical references (countries, regions, markets)
- **AMT** – Monetary amounts in different formats
- **PERSON** – Names of executives or individuals quoted

---

## 🔄 Workflow

1. **Annotation**
   - Annotate financial texts using [NER Annotator](https://github.com/jeniyat/ner-annotator) or a similar tool.
   - Export the annotated data in spaCy JSON format.

2. **Training**
   - Use the provided notebook to train the NER model with the annotated dataset.
   - Training is performed using spaCy’s standard NER pipeline (no transformer required).
   - Runs efficiently on CPU.

3. **Evaluation**
   - The model is evaluated using validation data.
   - Reports precision, recall, and F1-score metrics.

4. **Usage**
   - Deploy the trained model in financial analysis tools, contract parsing systems, or research projects.

---

## 💡 Example

**Input Text:**  
> Apple reported 25.3 billion U.S. dollars in Q1 2024, with Tim Cook emphasizing strong iPhone demand in Asia.

**Extracted Entities:**
- `ORG` – Apple
- `AMT` – 25.3 billion U.S. dollars
- `DATE` – Q1 2024
- `PERSON` – Tim Cook
- `PRODUCTS` – iPhone
- `LOCATION` – Asia

---

## 🛠️ Getting Started

1. **Open the CPU training notebook in Colab.**
2. **Upload your annotated JSON dataset.**
3. **Run the notebook cells step by step.**
4. **Save the trained model for later use.**

---

## 🧰 Tools Used

- [spaCy](https://spacy.io/) – For model training
- [Google Colab](https://colab.research.google.com/) (CPU runtime) – For running the training
- [NER Annotator](https://github.com/jeniyat/ner-annotator) – For preparing labeled datasets

---
>>>>>>> ec251f80b299dd35390e89eb474cc96f6d3dda4b
