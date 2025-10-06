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

# HuggingFace (BERT Sentiment)
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

app = Flask(__name__)
CORS(app)

# ------------------------
# Load SpaCy model (NER + sentence splitting)
# ------------------------
nlp = spacy.load("model-best")  # your trained SpaCy model folder

# Add sentence segmentation if missing (important for BERT sentence highlighting)
if "parser" not in nlp.pipe_names and "senter" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

# ------------------------
# Load LangExtract API key
# ------------------------
os.environ['LANGEXTRACT_API_KEY'] = "AIzaSyDtvWL0RmKWhlyMIKREWlxHA5w-fjFGYM0"

# ------------------------
# Load BERT Sentiment model
# ------------------------
bert_model_path = "bert_model"   # replace with your fine-tuned sentiment model path
tokenizer = AutoTokenizer.from_pretrained(bert_model_path)
model = AutoModelForSequenceClassification.from_pretrained(bert_model_path)
sentiment_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

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
# API Routes
# ------------------------

@app.route("/")
def home():
    return {"message": "Backend is running ✅"}

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
        # ------------------------
        # Docling extraction
        # ------------------------
        conversion_result = converter.convert(temp_path)
        text_content = conversion_result.document.export_to_text()
        if not text_content.strip():
            return jsonify({"error": "No text extracted from PDF."}), 400

        # ------------------------
        # SpaCy NER
        # ------------------------
        doc = nlp(text_content)
        spacy_html = spacy.displacy.render(doc, style="ent", jupyter=False)

        # ------------------------
        # BERT Sentiment Classification with Highlighting
        # ------------------------
        sentences = [sent.text.strip() for sent in doc.sents]

        highlighted_sentences = []
        for s in sentences:
            if not s:
                continue
            pred = sentiment_pipeline(s[:512])[0]  # truncate if too long
            label = pred["label"].lower()
            score = pred["score"]

            # Robust label mapping
            if "pos" in label or "label_2" in label:
                color = "#d4edda"   # green (positive)
            elif "neg" in label or "label_0" in label:
                color = "#f8d7da"   # red (negative)
            elif "neu" in label or "label_1" in label:
                color = "#fefefe"   # white (neutral)
            else:
                color = "white"

            highlighted_sentences.append(
                f'<span style="background-color:{color}; padding:2px; margin:2px; display:inline-block;" '
                f'title="{label} ({score:.2f})">{s}</span>'
            )

        bert_html = " ".join(highlighted_sentences)

        # ------------------------
        # LangExtract
        # ------------------------
        lang_entities = []
        lang_html_content = "<p>No LangExtract prompt provided.</p>"

        if user_prompt:
            if not user_example_json:
                return jsonify({"error": "LangExtract requires at least one example JSON"}), 400
            
            try:
                example_data_list = []
                parsed_examples = json.loads(user_example_json)
                for ex in parsed_examples:
                    extractions = [
                        Extraction(
                            extraction_class=e["field_name"],
                            extraction_text=str(e["value"]),
                            attributes={}
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

        # ------------------------
        # Return JSON response
        # ------------------------
        return jsonify({
            "fileName": file.filename,
            "raw_text": text_content,
            "spacy_html": spacy_html,
            "bert_html": bert_html,   # ✅ highlighted sentences
            "langextract_entities": lang_entities,
            "langextract_html": lang_html_content
        })

    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ------------------------
# Alias route for frontend (/process)
# ------------------------
@app.route("/process", methods=["POST"])
def process_alias():
    return extract_text()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
