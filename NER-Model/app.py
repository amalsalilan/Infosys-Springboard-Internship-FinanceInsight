import torch # type: ignore
from fastapi import FastAPI, UploadFile, File, Form, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from transformers import BertTokenizer, BertForSequenceClassification # type: ignore
from fastapi.middleware.cors import CORSMiddleWARE # type: ignore
import uvicorn # type: ignore
import io
import docx # type: ignore
import pypdf # type: ignore
import re
import os
import json
import textwrap
from typing import Optional, List

# NLP Libraries
import spacy # type: ignore 
import langextract as lx # type: ignore
import google.generativeai as genai

# --- 1. TRAINED LANGEXTRACT MODEL CLASS ---
class FinancialEntityExtractor:
    """Trained LangExtract model for financial entity extraction"""
    
    def __init__(self, api_key=None):
        # Fallback API Key for the pre-configured model
        self.api_key = api_key or os.getenv("LANGEXTRACT_API_KEY", "AIzaSyD-JzTTvGVL4uDE5ABFKMJniQBzJm6ZVXg")
        os.environ["LANGEXTRACT_API_KEY"] = self.api_key
        
        # Model configuration
        self.model_id = "gemini-2.5-flash"
        self.max_workers = 1
        
        # Define extraction schema
        self.prompt = textwrap.dedent("""\
            Extract financial entities from the document in order of appearance.
            
            Entity Types:
            - company_name: Any company, corporation, or business entity
            - person_name: Names of executives, analysts, or individuals mentioned
            - financial_metric: Revenue, profit, earnings, stock prices, percentages, growth rates
            - product: Products, services, or product lines
            - location: Geographic locations, markets, regions
            - date: Specific dates or time periods mentioned
            
            Rules:
            1. Use exact text from document (no paraphrasing)
            2. Extract in order of appearance
            3. Provide contextual attributes for each entity
            4. Avoid overlapping extractions
        """)
        
        # Training examples for better accuracy
        self.examples = [
            lx.data.ExampleData(
                text=(
                    "Apple Inc reported Q4 revenue of $89.5 billion, a 12% increase. "
                    "CEO Tim Cook announced the new iPhone 15 Pro will launch in Cupertino."
                ),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="company_name",
                        extraction_text="Apple Inc",
                        attributes={"ceo": "Tim Cook", "location": "Cupertino"},
                    ),
                    lx.data.Extraction(
                        extraction_class="financial_metric",
                        extraction_text="$89.5 billion",
                        attributes={"type": "revenue", "period": "Q4"},
                    ),
                    lx.data.Extraction(
                        extraction_class="financial_metric",
                        extraction_text="12%",
                        attributes={"type": "growth_rate"},
                    ),
                    lx.data.Extraction(
                        extraction_class="person_name",
                        extraction_text="Tim Cook",
                        attributes={"title": "CEO", "company": "Apple Inc"},
                    ),
                    lx.data.Extraction(
                        extraction_class="product",
                        extraction_text="iPhone 15 Pro",
                        attributes={"company": "Apple Inc"},
                    ),
                    lx.data.Extraction(
                        extraction_class="location",
                        extraction_text="Cupertino",
                        attributes={"company": "Apple Inc"},
                    ),
                ],
            ),
            lx.data.ExampleData(
                text=(
                    "Tesla missed earnings expectations with EPS of $0.85. "
                    "Analysts at Goldman Sachs downgraded the stock in January 2024."
                ),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="company_name",
                        extraction_text="Tesla",
                    ),
                    lx.data.Extraction(
                        extraction_class="financial_metric",
                        extraction_text="$0.85",
                        attributes={"type": "EPS"},
                    ),
                    lx.data.Extraction(
                        extraction_class="company_name",
                        extraction_text="Goldman Sachs",
                        attributes={"type": "investment_bank"},
                    ),
                    lx.data.Extraction(
                        extraction_class="date",
                        extraction_text="January 2024",
                    ),
                ],
            ),
        ]
        
        # Model configuration
        self.config = {
            "model_id": self.model_id,
            "max_workers": self.max_workers,
            "prompt": self.prompt,
            "entity_classes": [
                "company_name",
                "person_name", 
                "financial_metric",
                "product",
                "location",
                "date"
            ],
            "version": "1.0.0"
        }
        
        print("✓ Financial Entity Extractor initialized")
        print(f"✓ Entity classes: {', '.join(self.config['entity_classes'])}")
    
    def extract(self, text, custom_prompt=None):
        """Run extraction on input text"""
        try:
            # Use custom prompt if provided, otherwise use the default trained prompt
            prompt_to_use = custom_prompt if custom_prompt else self.prompt
            
            result = lx.extract(
                text_or_documents=text,
                prompt_description=prompt_to_use,
                examples=self.examples,
                model_id=self.model_id,
                max_workers=self.max_workers,
            )
            return self._format_results(result)
        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")
    
    def _format_results(self, result):
        """Format extraction results into structured output"""
        formatted = {
            "entities": {},
            "all_extractions": []
        }
        
        # Initialize entity type lists
        for entity_type in self.config["entity_classes"]:
            formatted["entities"][entity_type] = []
        
        # Process extractions
        for ex in result.extractions:
            # Handle char_interval safely
            try:
                if hasattr(ex.char_interval, 'start') and hasattr(ex.char_interval, 'end'):
                    position = {
                        "start": ex.char_interval.start,
                        "end": ex.char_interval.end
                    }
                elif isinstance(ex.char_interval, (list, tuple)) and len(ex.char_interval) >= 2:
                    position = {
                        "start": ex.char_interval[0],
                        "end": ex.char_interval[1]
                    }
                else:
                    position = {"start": 0, "end": 0}
            except:
                position = {"start": 0, "end": 0}
            
            entity_data = {
                "text": ex.extraction_text,
                "type": ex.extraction_class,
                "attributes": ex.attributes or {},
                "position": position
            }
            
            # Add to type-specific list
            if ex.extraction_class in formatted["entities"]:
                formatted["entities"][ex.extraction_class].append(entity_data)
            
            # Add to all extractions
            formatted["all_extractions"].append(entity_data)
        
        # Add summary statistics
        formatted["summary"] = {
            "total_extractions": len(result.extractions),
            "counts": {
                entity_type: len(formatted["entities"][entity_type])
                for entity_type in self.config["entity_classes"]
            }
        }
        
        return formatted


# --- 2. SETUP ---
app = FastAPI(title="Financial Insight API")

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. MODEL AND CONFIGURATION LOADING (GLOBAL) ---

# Load BERT Model (Sentiment)
print("Loading BERT model...")
try:
    model_save_path = './financial_bert_model'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    bert_model = BertForSequenceClassification.from_pretrained(model_save_path)
    bert_tokenizer = BertTokenizer.from_pretrained(model_save_path)
    
    bert_model = bert_model.to(device)
    bert_model.eval()
    
    label_names = ['Positive', 'Negative', 'Neutral']
    max_length = 128
    
    print(f"✓ BERT model loaded successfully on device: {device}")
except Exception as e:
    print(f"⚠ Could not load BERT model. Error: {e}")
    bert_model = None
    bert_tokenizer = None

# Load SpaCy Model (General NER)
print("Loading SpaCy NER model...")
SPACY_MODEL_NAME = 'en_core_web_md'

try:
    nlp_spacy = spacy.load(SPACY_MODEL_NAME)
    print(f"✓ SpaCy NER model loaded: {SPACY_MODEL_NAME}")
except Exception as e:
    print(f"⚠ Could not load SpaCy model. Error: {e}")
    nlp_spacy = None 

# Initialize Trained LangExtract Model
print("Initializing trained LangExtract model...")
try:
    financial_extractor = FinancialEntityExtractor()
    print("✓ LangExtract Financial Entity Extractor ready")
except Exception as e:
    print(f"⚠ Could not initialize LangExtract model: {e}")
    financial_extractor = None

# Configure Gemini for fallback
print("Configuring Gemini API...")
gemini_model = None
available_models = []

try:
    DEFAULT_API_KEY = os.getenv("LANGEXTRACT_API_KEY", "AIzaSyD-JzTTvGVL4uDE5ABFKMJniQBzJm6ZVXg")
    genai.configure(api_key=DEFAULT_API_KEY)
    
    try:
        available_models = [m.name for m in genai.list_models()]
        print(f"✓ Available Gemini models: {len(available_models)} models found")
    except Exception as e:
        print(f"⚠ Could not list models: {e}")
        available_models = ["models/gemini-2.5-flash", "models/gemini-1.5-pro"]
    
except Exception as e:
    print(f"⚠ Gemini configuration failed: {e}")


# --- 4. HELPER FUNCTIONS FOR FILE READING ---

def read_pdf(file_stream: io.BytesIO) -> str:
    """Reads and extracts text from a PDF file stream."""
    try:
        reader = pypdf.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        # Re-raise as HTTPException for consistent FastAPI error handling
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {e}")

def read_docx(file_stream: io.BytesIO) -> str:
    """Reads and extracts text from a DOCX file stream."""
    try:
        document = docx.Document(file_stream)
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {e}")

def read_txt(file_stream: io.BytesIO) -> str:
    """Reads text from a TXT file stream."""
    try:
        return file_stream.read().decode('utf-8')
    except Exception as e:
        try:
            file_stream.seek(0)
            return file_stream.read().decode('latin-1')
        except:
            raise HTTPException(status_code=400, detail=f"Error reading TXT file with common encodings.")

def split_into_sentences(text: str):
    """Splits text into sentences using a simple regex."""
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


# --- 5. ENDPOINT: BERT SENTIMENT PREDICTION (/predict_file) ---

@app.post("/predict_file")
async def predict_sentiment_from_file(
    file: UploadFile = File(...), 
    sentiment_filter: str = Form("all")
):
    """Accepts a file and performs sentiment analysis on each sentence (BERT)."""
    if not bert_model or not bert_tokenizer:
        raise HTTPException(status_code=503, detail="Sentiment model is not available.")
    
    file_bytes = await file.read()
    file_stream = io.BytesIO(file_bytes)
    filename = file.filename or "unknown"
    
    # Extract text based on file type
    if filename.endswith(".pdf"):
        document_text = read_pdf(file_stream)
    elif filename.endswith(".docx"):
        document_text = read_docx(file_stream)
    elif filename.endswith(".txt"):
        file_stream.seek(0)
        document_text = read_txt(file_stream)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT.")

    if not document_text.strip():
        raise HTTPException(status_code=400, detail="The document appears to be empty.")

    sentences = split_into_sentences(document_text)
    results = []
    
    for sentence in sentences:
        if not sentence:
            continue

        inputs = bert_tokenizer(
            sentence,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors='pt'
        ).to(device)

        with torch.no_grad():
            outputs = bert_model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
            
            predicted_class_idx = torch.argmax(probs).item()
            predicted_sentiment = label_names[predicted_class_idx]
            confidence = probs[predicted_class_idx].item()
        
        if sentiment_filter == 'all' or sentiment_filter.lower() == predicted_sentiment.lower():
            results.append({
                "sentence": sentence,
                "sentiment": predicted_sentiment,
                "confidence": round(confidence * 100, 2)
            })

    return {
        "filename": filename,
        "total_sentences_processed": len(sentences),
        "filter_applied": sentiment_filter,
        "analysis_results": results
    }


# --- 6. ENDPOINT: SPACY GENERAL NER (/predict_spacy) ---

class SpacyExtractionResult(BaseModel):
    extraction_text: str
    extraction_class: str
    start_char: int
    end_char: int

class SpacyResponse(BaseModel):
    filename: str
    total_entities_found: int
    extraction_results: List[SpacyExtractionResult]


@app.post("/predict_spacy", response_model=SpacyResponse)
async def predict_entities_from_file(file: UploadFile = File(...)):
    """Performs general Named Entity Recognition using SpaCy."""
    if nlp_spacy is None:
        raise HTTPException(status_code=503, detail="SpaCy NER model is not loaded.")

    file_bytes = await file.read()
    file_stream = io.BytesIO(file_bytes)
    filename = file.filename or "unknown"
    
    # Extract text
    if filename.endswith(".pdf"):
        document_text = read_pdf(file_stream)
    elif filename.endswith(".docx"):
        document_text = read_docx(file_stream)
    elif filename.endswith(".txt"):
        file_stream.seek(0)
        document_text = read_txt(file_stream)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    if not document_text.strip():
        raise HTTPException(status_code=400, detail="Document is empty.")

    doc = nlp_spacy(document_text)

    results = [
        {
            "extraction_text": ent.text,
            "extraction_class": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char,
        }
        for ent in doc.ents
    ]

    return {
        "filename": filename,
        "total_entities_found": len(results),
        "extraction_results": results,
    }


# --- 7. NEW ENDPOINT: TRAINED LANGEXTRACT MODEL (/extract_trained) ---

class TrainedExtractionResponse(BaseModel):
    filename: str
    total_characters_processed: int
    entities: dict
    summary: dict
    all_extractions: List[dict]

@app.post("/extract_trained", response_model=TrainedExtractionResponse)
async def extract_with_trained_model(
    file: UploadFile = File(...),
    # custom_prompt is OPTIONAL here, the default financial prompt is used if none is provided
    custom_prompt: Optional[str] = Form(None) 
):
    """
    Extract financial entities using the trained LangExtract model.
    No API key required from the user; it uses the pre-configured model's key.
    """
    if not financial_extractor:
        raise HTTPException(status_code=503, detail="Financial extractor model not available.")
    
    file_bytes = await file.read()
    file_stream = io.BytesIO(file_bytes)
    filename = file.filename or "unknown"

    # Extract text
    if filename.endswith(".pdf"):
        document_text = read_pdf(file_stream)
    elif filename.endswith(".docx"):
        document_text = read_docx(file_stream)
    elif filename.endswith(".txt"):
        file_stream.seek(0)
        document_text = read_txt(file_stream)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    if not document_text.strip():
        raise HTTPException(status_code=400, detail="Document is empty.")

    # Extract using trained model
    try:
        results = financial_extractor.extract(document_text, custom_prompt)
        
        return {
            "filename": filename,
            "total_characters_processed": len(document_text),
            "entities": results["entities"],
            "summary": results["summary"],
            "all_extractions": results["all_extractions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


# --- 8. ENDPOINT: LANGEXTRACT WITH CUSTOM PROMPT (/extract_file) ---

class ExtractionResult(BaseModel):
    extraction_class: str
    extraction_text: str
    attributes: dict

class LangExtractResponse(BaseModel):
    filename: str
    total_characters_processed: int
    extraction_results: List[ExtractionResult]


@app.post("/extract_file", response_model=LangExtractResponse)
async def extract_data_from_file(
    file: UploadFile = File(...),
    # API key and prompt are MANDATORY for this custom LLM endpoint
    api_key: str = Form(...), 
    prompt_description: str = Form(...)
):
    """
    Extract entities using LangExtract with a custom prompt.
    Requires API key and custom prompt from the user.
    """
    # The Form(...) declaration already makes it required, 
    # but an explicit check is good if empty strings are sent.
    if not api_key or not prompt_description:
        raise HTTPException(status_code=400, detail="API Key and Prompt Description are required.")

    file_bytes = await file.read()
    file_stream = io.BytesIO(file_bytes)
    filename = file.filename or "unknown"

    # Extract text
    if filename.endswith(".pdf"):
        document_text = read_pdf(file_stream)
    elif filename.endswith(".docx"):
        document_text = read_docx(file_stream)
    elif filename.endswith(".txt"):
        file_stream.seek(0)
        document_text = read_txt(file_stream)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    if not document_text.strip():
        raise HTTPException(status_code=400, detail="Document is empty.")

    # Temporarily set the provided API key for the LangExtract call
    os.environ["LANGEXTRACT_API_KEY"] = api_key
    
    # Try extraction with model fallback
    try:
        model_attempts = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        result = None
        
        for model_id in model_attempts:
            try:
                result = lx.extract(
                    text_or_documents=document_text,
                    prompt_description=prompt_description,
                    model_id=model_id,
                    max_workers=1,
                )
                break
            except Exception:
                continue
        
        if result is None:
            raise Exception("All model attempts failed or API Key is invalid.")
            
    except Exception as e:
        # Revert environment variable after use (or handle key storage securely)
        os.environ["LANGEXTRACT_API_KEY"] = financial_extractor.api_key if financial_extractor else "" 
        raise HTTPException(status_code=500, detail=f"Extraction Error: {e}")

    # Revert environment variable after use
    os.environ["LANGEXTRACT_API_KEY"] = financial_extractor.api_key if financial_extractor else ""

    extraction_results = [
        {
            "extraction_class": ex.extraction_class,
            "extraction_text": ex.extraction_text,
            "attributes": ex.attributes or {},
        }
        for ex in result.extractions
    ]
    
    return {
        "filename": filename,
        "total_characters_processed": len(document_text),
        "extraction_results": extraction_results
    }


# --- 9. ENDPOINT: GET MODEL INFO (/model_info) ---

class ModelStatus(BaseModel):
    name: str
    loaded: bool
    details: Optional[str] = None

class ModelInfoResponse(BaseModel):
    bert_sentiment: ModelStatus
    spacy_ner: ModelStatus
    langextract_trained: ModelStatus
    available_entity_types: List[str]

@app.get("/model_info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about all loaded models"""
    entity_types = []
    if financial_extractor:
        entity_types = financial_extractor.config["entity_classes"]
    
    return {
        "bert_sentiment": ModelStatus(
            name="BERT Sentiment Analysis",
            loaded=bert_model is not None,
            details=f"Device: {device}" if bert_model else "Not loaded"
        ),
        "spacy_ner": ModelStatus(
            name="SpaCy NER",
            loaded=nlp_spacy is not None,
            details=SPACY_MODEL_NAME if nlp_spacy else "Not loaded"
        ),
        "langextract_trained": ModelStatus(
            name="Financial Entity Extractor (Trained)",
            loaded=financial_extractor is not None,
            details=f"Model: {financial_extractor.model_id}" if financial_extractor else "Not loaded"
        ),
        "available_entity_types": entity_types
    }


# --- 10. RUN THE API ---
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 FINANCIAL INSIGHT API - READY")
    print("="*70)
    print(f"✓ BERT Sentiment Model: {'Loaded' if bert_model else 'Not available'}")
    print(f"✓ SpaCy NER Model: {'Loaded' if nlp_spacy else 'Not available'}")
    print(f"✓ Trained Financial Extractor: {'Loaded' if financial_extractor else 'Not available'}")
    if financial_extractor:
        print(f"  - Entity types: {', '.join(financial_extractor.config['entity_classes'])}")
    print("="*70 + "\n")
    
    print("📡 Available Endpoints:")
    print("  POST /predict_file      - BERT sentiment analysis")
    print("  POST /predict_spacy      - SpaCy NER extraction")
    print("  POST /extract_trained    - Trained financial entity extraction")
    print("  POST /extract_file       - Custom prompt extraction (Requires API Key)")
    print("  GET  /model_info         - Model status information")
    print("  GET  /docs               - API documentation")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)