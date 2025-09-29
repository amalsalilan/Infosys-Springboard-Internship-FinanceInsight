#  Financial Document Analysis AI

A powerful full-stack application designed to extract, analyze, and visualize information from financial documents. This tool leverages a suite of advanced AI libraries to process both digital and scanned PDFs, providing structured data and insights through a clean, modern user interface.

## ✨ Features

* **Advanced Document Parsing:** Utilizes the `docling` library to handle both digital and scanned PDFs, with OCR capabilities for image-based documents.
* **Named Entity Recognition (NER):** Employs a custom-trained `spaCy` model (`best_finance_ner_model`) to identify and extract key financial entities.
* **Prompt-Based Extraction:** Integrates `langextract` to perform targeted, few-shot extraction based on user-defined prompts and examples.
* **Interactive Visualizations:** Renders extracted entities from both SpaCy and LangExtract in a clear, easy-to-read HTML format.
* **Full-Stack Architecture:** Built with a robust Flask backend for AI processing and a responsive React frontend for a seamless user experience.

---

## 🚀 Tech Stack

| Component | Technology / Library |
| :--- | :--- |
| **Backend** | 🐍 Python, Flask, Docling, SpaCy, LangExtract, PyTorch |
| **Frontend**| ⚛️ React, Tailwind CSS, Axios |
| **AI Models** | Custom SpaCy NER, Google's Gemini (via LangExtract) |

---

## 📂 Project Structure

The project uses a standard monorepo structure with two distinct parts: `backend` and `frontend`.
