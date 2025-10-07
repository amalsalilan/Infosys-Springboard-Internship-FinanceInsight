from docling.document_converter import DocumentConverter

# Input PDF (contract, agreement, financial report)
source = r"C:\Users\girid\OneDrive\Desktop\FinanceInsightRegex\Contract_Agreement_Summary.pdf"

# Initialize Docling converter
converter = DocumentConverter()

# Convert PDF
result = converter.convert(source)

# Save extracted text to a .txt file
output_path = r"C:\Users\girid\OneDrive\Desktop\FinanceInsightRegex\Contract_Agreement_Summary.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())

print(f"✅ Converted! Extracted text saved to: "C:\Users\girid\OneDrive\Desktop\FinanceInsightRegex\extracted_entities_refined.txt"")
