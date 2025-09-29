# import fitz  # PyMuPDF
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# # Initialize the Flask application
# app = Flask(__name__)

# # Enable Cross-Origin Resource Sharing (CORS) to allow your frontend to connect
# CORS(app)

# @app.route('/api/extract-text', methods=['POST'])
# def extract_text():
#     """API endpoint to extract text from an uploaded PDF file."""
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part in the request"}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({"error": "No file selected for uploading"}), 400

#     if file and file.filename.lower().endswith('.pdf'):
#         try:
#             pdf_document = fitz.open(stream=file.read(), filetype="pdf")
#             extracted_text = ""
#             for page in pdf_document:
#                 extracted_text += page.get_text()

#             pdf_document.close()

#             return jsonify({
#                 "fileName": file.filename,
#                 "extractedText": extracted_text
#             })

#         except Exception as e:
#             return jsonify({"error": f"An error occurred: {str(e)}"}), 500
#     else:
#         return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400

# # This runs the app
# if __name__ == '__main__':
#     app.run(port=5000, debug=True)




# Wrong code from gemini
# import docling
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# # Initialize the Flask application
# app = Flask(__name__)
# CORS(app)

# @app.route('/api/extract-text', methods=['POST'])
# def extract_text():
#     """API endpoint to extract text using the docling library."""
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part in the request"}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({"error": "No file selected for uploading"}), 400

#     try:
#         # Read the file's bytes directly from the request
#         file_bytes = file.read()

#         # Use docling to parse the file bytes
#         # Docling automatically handles OCR for images and scanned PDFs
#         parsed_doc = docling.parse(file_bytes)

#         # Convert the parsed document into plain text
#         text_content = parsed_doc.to_text()

#         if not text_content.strip():
#              return jsonify({"error": "Docling could not extract any text from the file."}), 400

#         return jsonify({
#             "fileName": file.filename,
#             "extractedText": text_content
#         })

#     except Exception as e:
#         # This will catch errors from the docling library if a file is unsupported or corrupt
#         return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500

# # This runs the app
# if __name__ == '__main__':
#     app.run(port=5000, debug=True)




# import os
# import tempfile
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch

# # Docling imports
# from docling.datamodel.pipeline_options import PdfPipelineOptions
# from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption
# from docling_ocr_onnxtr import OnnxtrOcrOptions

# app = Flask(__name__)
# CORS(app)

# # ✅ Configure OCR options
# ocr_options = OnnxtrOcrOptions(
#     det_arch="db_mobilenet_v3_large",
#     reco_arch="Felix92/onnxtr-parseq-multilingual-v1",
#     auto_correct_orientation=False
# )

# pipeline_options = PdfPipelineOptions(ocr_options=ocr_options)
# pipeline_options.allow_external_plugins = True

# converter = DocumentConverter(
#     format_options={
#         InputFormat.PDF: PdfFormatOption(
#             pipeline_options=pipeline_options,
#         )
#     },
# )

# print("CUDA available:", torch.cuda.is_available())
# if torch.cuda.is_available():
#     print("Using GPU:", torch.cuda.get_device_name(0))
# else:
#     print("Running on CPU (OCR will be slower).")


# @app.route('/api/extract-text', methods=['POST'])
# def extract_text():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part in the request"}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({"error": "No file selected for uploading"}), 400

#     try:
#         # ✅ Create a temporary file in the system's temp directory
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#             temp_path = tmp.name
#             file.save(temp_path)

#         # Run Docling conversion
#         conversion_result = converter.convert(source=temp_path)

#         # Extract plain text
#         text_content = conversion_result.document.export_to_text()

#         if not text_content.strip():
#             return jsonify({"error": "Docling could not extract any text from the file."}), 400

#         return jsonify({
#             "fileName": file.filename,
#             "extractedText": text_content
#         })

#     except Exception as e:
#         return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500
#     finally:
#         # ✅ Clean up temp file if it exists
#         if 'temp_path' in locals() and os.path.exists(temp_path):
#             os.remove(temp_path)


# if __name__ == '__main__':
#     app.run(port=5000, debug=True)


# # FINAL
# import os
# import tempfile
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import torch

# from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption
# from docling.datamodel.pipeline_options import PdfPipelineOptions

# # Try to import OCR plugin
# try:
#     from docling_ocr_onnxtr import OnnxtrOcrOptions
#     ocr_enabled = True
# except ImportError:
#     print("⚠️ OCR plugin not installed. Will parse PDFs without OCR.")
#     ocr_enabled = False

# # Initialize Flask
# app = Flask(__name__)
# CORS(app)

# # Configure OCR pipeline if plugin available
# if ocr_enabled:
#     ocr_options = OnnxtrOcrOptions(
#         det_arch="db_mobilenet_v3_large",
#         reco_arch="Felix92/onnxtr-parseq-multilingual-v1",
#         auto_correct_orientation=False
#     )
#     pipeline_options = PdfPipelineOptions(ocr_options=ocr_options)
#     pipeline_options.allow_external_plugins = True
# else:
#     pipeline_options = PdfPipelineOptions()  # empty options if no OCR

# # Create converter for PDF input
# converter = DocumentConverter(
#     format_options={
#         InputFormat.PDF: PdfFormatOption(
#             pipeline_options=pipeline_options
#         )
#     }
# )

# print("CUDA available:", torch.cuda.is_available())
# if torch.cuda.is_available():
#     print("GPU device:", torch.cuda.get_device_name(0))


# @app.route("/api/extract-text", methods=["POST"])
# def extract_text():
#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "Empty filename"}), 400

#     # Save file temporarily
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         temp_path = tmp.name
#         file.save(temp_path)

#     try:
#         # Convert PDF with Docling
#         conversion_result = converter.convert(temp_path)
#         text_content = conversion_result.document.export_to_text()

#         if not text_content.strip():
#             return jsonify({"error": "No text could be extracted from this PDF."}), 400

#         return jsonify({"fileName": file.filename, "extractedText": text_content})

#     except Exception as e:
#         return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500

#     finally:
#         # Clean up temp file
#         if os.path.exists(temp_path):
#             os.remove(temp_path)


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)



# FINAL WITH SPACY AND LANGEXTRACT
import os
import tempfile
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import spacy
import langextract as lx
from langextract.data import ExampleData, Extraction

from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

app = Flask(__name__)
CORS(app)

# ------------------------
# Load SpaCy model
# ------------------------
nlp = spacy.load("best_finance_ner_model")  # your trained SpaCy model folder

# ------------------------
# Load LangExtract API key
# ------------------------
# Replace with your actual key or load from environment variables for security
os.environ['LANGEXTRACT_API_KEY'] = "api_key_from_dot_env"

# ------------------------
# Docling PDF converter
# ------------------------
try:
    from docling_ocr_onnxtr import OnnxtrOcrOptions
    ocr_enabled = True
    print("✅ OCR plugin found. GPU-accelerated OCR is enabled.")
except ImportError:
    print("⚠️ OCR plugin not installed. Parsing PDFs without OCR.")
    ocr_enabled = False

if ocr_enabled and torch.cuda.is_available():
    print(f"GPU device found: {torch.cuda.get_device_name(0)}. Using GPU for OCR.")
    ocr_options = OnnxtrOcrOptions(
        det_arch="db_mobilenet_v3_large",
        reco_arch="Felix92/onnxtr-parseq-multilingual-v1",
        auto_correct_orientation=False
    )
    pipeline_options = PdfPipelineOptions(ocr_options=ocr_options)
    pipeline_options.allow_external_plugins = True
else:
    if ocr_enabled:
        print("CUDA not available. Falling back to CPU for OCR.")
    pipeline_options = PdfPipelineOptions()

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

# ------------------------
# API Route
# ------------------------
@app.route("/api/extract-text", methods=["POST"])
def extract_text():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    user_prompt = request.form.get("langextract_prompt", None)
    user_example_json = request.form.get("langextract_example", None)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        temp_path = tmp.name
        file.save(temp_path)

    try:
        # Docling extraction
        conversion_result = converter.convert(temp_path)
        text_content = conversion_result.document.export_to_text()
        if not text_content.strip():
            return jsonify({"error": "No text extracted from PDF."}), 400

        # SpaCy NER
        doc = nlp(text_content)
        spacy_html = spacy.displacy.render(doc, style="ent", jupyter=False)

        # LangExtract
        lang_entities = []
        lang_html_content = "<p>No LangExtract prompt provided.</p>"

        if user_prompt:
            if not user_example_json:
                return jsonify({"error": "LangExtract requires at least one example JSON"}), 400
            
            try:
                example_data_list = []
                parsed_examples = json.loads(user_example_json)
                for ex in parsed_examples:
                    # CORRECTED: Use 'extraction_class' and 'extraction_text' with optional 'attributes'
                    extractions = [
                        Extraction(
                            extraction_class=e["field_name"],
                            extraction_text=str(e["value"]),
                            attributes={}  # Can add attributes here if needed
                        ) 
                        for e in ex["extractions"]
                    ]
                    example_data_list.append(ExampleData(text=ex["text"], extractions=extractions))

                lang_result = lx.extract(
                    text_or_documents=text_content,
                    prompt_description=user_prompt,
                    examples=example_data_list,
                    model_id="gemini-2.5-flash"
                )

                # Convert extractions to dictionaries
                lang_entities = []
                for e in lang_result.extractions:
                    entity_dict = {
                        "extraction_class": e.extraction_class,
                        "extraction_text": e.extraction_text,
                        "start_char": getattr(e, 'start_char', None),
                        "end_char": getattr(e, 'end_char', None),
                    }
                    if hasattr(e, 'attributes') and e.attributes:
                        entity_dict["attributes"] = e.attributes
                    lang_entities.append(entity_dict)
                lang_html_obj = lx.visualize(lang_result)
                lang_html_content = lang_html_obj.data if hasattr(lang_html_obj, 'data') else str(lang_html_obj)

            except Exception as e:
                return jsonify({"error": f"Error processing LangExtract example: {str(e)}"}), 500

        return jsonify({
            "fileName": file.filename,
            "raw_text": text_content,
            "spacy_html": spacy_html,
            "langextract_entities": lang_entities,
            "langextract_html": lang_html_content
        })

    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)