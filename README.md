NER + PDF Parsing

This project extracts key details from resumes in PDF format, such as name, email, phone number, skills, degree, university, and graduation year, using Natural Language Processing (NLP) techniques with spaCy and pdfplumber.

Key Features:

Uses pdfplumber to read and extract text from PDF resumes.
Applies spaCy Named Entity Recognition (NER) to identify important entities.
Custom parsing logic to extract structured details from unstructured resume data.
Generates a structured JSON/dictionary output for further use in job-matching or analytics.

Workflow:
Load the resume PDF.
Extract raw text using pdfplumber.
Process the text with spaCy NLP model (en_core_web_trf).
Identify and extract key details (Name, Email, Phone, Skills, Education, etc.).
Return the information in a structured format.
