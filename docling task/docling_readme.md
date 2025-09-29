## Overview
This project demonstrates how to extract structured text and tables from PDF documents using Python. It leverages the Docling library to convert PDFs into structured formats, including plain text and tables.

## Features Implemented
- PDF conversion to text using `DocumentConverter` from Docling.
- Optional OCR handling (disabled for this project).
- Table structure extraction using `TableFormerMode.FAST` for speed.
- Cell matching in tables for improved structure recognition.
- Exported the converted document to a `.txt` file.

## Tools & Libraries
- **Python 3.12**  
- **Docling** – PDF and document conversion.  
- **Langextract** – Language detection.  
- **pypdf, python-docx, python-pptx** – Handling PDFs, Word, and PowerPoint files.  
- **pypdfium2 and EasyOCR** – Optional support for OCR-based text extraction.

## How to Run
1. Install dependencies:
```bash
pip install docling langextract pypdf
````

2. Set your API key:

```python
import os
os.environ['LANGEXTRACT_API_KEY'] = "YOUR_API_KEY"
```

3. Specify your input PDF and run the conversion script:

```python
input_doc_path = "/path/to/Annual Report 2024-25 (English).pdf"
```

4. Extracted text and table data will be saved to `scratch/` directory.

## Outcome

* Successfully extracted text from **Annual Report 2024-25** 332 pages pdf.
* Tables in the PDF were identified and structured efficiently.
* Conversion completed in approximately **188 seconds**.

`
