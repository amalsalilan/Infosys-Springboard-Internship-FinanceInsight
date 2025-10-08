from docling.document_converter import DocumentConverter
import os

# Define input & output paths
BASE_DIR = r"C:\Users\girid\OneDrive\Desktop\FinanceInsightRegex"
input_pdf = os.path.join(BASE_DIR, "Contract_Agreement_Summary.pdf")
output_txt = os.path.join(BASE_DIR, "Contract_Agreement_Summary.txt")

# Initialize and run Docling converter
try:
    converter = DocumentConverter()
    result = converter.convert(input_pdf)

    with open(output_txt, "w", encoding="utf-8") as file:
        file.write(result.document.export_to_markdown())

    print(f"✅ PDF successfully converted. Extracted text saved at: {output_txt}")

except Exception as e:
    print(f"❌ Conversion failed: {e}")