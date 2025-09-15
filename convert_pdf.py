#Importing required libraries
from docling.document_converter import DocumentConverter
from pathlib import Path

#Defining input & output paths
BASE_DIR = Path(r"C:\Users\Bindu\OneDrive\Desktop\Infosys")
input_pdf = BASE_DIR / "Sample_Contract.pdf"
output_txt = BASE_DIR / "Sample_Contract.pdf.txt"

#Convert PDF → Text
try:
    print("Starting conversion...")

    converter = DocumentConverter()
    result = converter.convert(str(input_pdf))

    extracted_text = result.document.export_to_markdown()

    # Save to TXT file
    output_txt.write_text(extracted_text, encoding="utf-8")

    print(f"PDF successfully converted!")
    print(f"Extracted text saved at: {output_txt}")

    # Optional: Print preview (first 20 lines)
    print("\nPreview of extracted content:\n")
    for line in extracted_text.splitlines()[:20]:
        print(line)

except Exception as e:
    print(f"Conversion failed. Error: {e}")
