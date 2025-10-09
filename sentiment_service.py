#sentiment_service.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import re
import logging
import sys
import warnings
from bs4 import BeautifulSoup
from pathlib import Path
import os

# Optional torch (graceful on Python 3.13 if wheels are missing)
try:
    import torch  # type: ignore
    TORCH_AVAILABLE = True
except Exception:
    torch = None  # type: ignore
    TORCH_AVAILABLE = False

# Suppress warnings from external libraries
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*resume_download.*")

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/sentiment_service.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentiment Analysis Service",
    description="API for analyzing sentiment in financial documents using FinBERT",
    version="1.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", "http://127.0.0.1:8080",
        "http://localhost:3000", "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Global state
# --------------------
# Defaults + catalog
DEFAULT_BERT_CHOICES = [
    os.getenv("FINBERT_MODEL", "ProsusAI/finbert"),
    "yiyanghkust/finbert-tone",
]
BERT_CATALOG: List[str] = sorted(list({*DEFAULT_BERT_CHOICES}))

ACTIVE_MODEL_NAME: Optional[str] = os.getenv("FINBERT_MODEL", "ProsusAI/finbert")

# Global tokenizer/model/pipeline
model = None
tokenizer = None
hf_pipeline = None  # we’ll use pipeline for robust labels
id2label_norm: Dict[int, str] = {}  # normalized id2label


# --------------------
# Schemas
# --------------------
class SentimentRequest(BaseModel):
    text: str
    html: Optional[str] = None


class SentimentResult(BaseModel):
    sentence: str
    class_: str
    position: Dict[str, int]
    confidence_scores: Dict[str, float]

    class Config:
        fields = {'class_': 'class'}


class SentimentResponse(BaseModel):
    sentiment_results: List[Dict]
    highlighted_html: Optional[str] = None


class ActivateRequest(BaseModel):
    name: Optional[str] = None


class HFRequest(BaseModel):
    repo: str


# --------------------
# Helpers
# --------------------
def _norm_label(lbl: str) -> str:
    l = (lbl or "").lower()
    if "pos" in l:
        return "positive"
    if "neg" in l:
        return "negative"
    if "neu" in l:
        return "neutral"
    return l


def _build_id2label_norm(m) -> Dict[int, str]:
    mapping = {}
    try:
        raw = getattr(m.config, "id2label", None)
        if isinstance(raw, dict):
            for k, v in raw.items():
                try:
                    mapping[int(k)] = _norm_label(v)
                except Exception:
                    continue
    except Exception:
        pass
    # Fallback if config missing
    if not mapping and hasattr(m, "num_labels"):
        n = m.num_labels
        default = ["positive", "negative", "neutral"][:n]
        mapping = {i: default[i] for i in range(n)}
    return mapping


def _load_model(name: str):
    global tokenizer, model, hf_pipeline, id2label_norm, ACTIVE_MODEL_NAME
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is not available in this Python environment.")
    logger.info("Loading tokenizer: %s", name)
    tokenizer = AutoTokenizer.from_pretrained(name)
    logger.info("Loading model: %s", name)
    model = AutoModelForSequenceClassification.from_pretrained(name)
    id2label_norm = _build_id2label_norm(model)
    # Build a pipeline to ensure label text aligns with model config
    device = 0 if TORCH_AVAILABLE and torch.cuda.is_available() else -1  # type: ignore
    hf_pipeline = pipeline(
        "text-classification", model=model, tokenizer=tokenizer, device=device, truncation=True
    )
    ACTIVE_MODEL_NAME = name
    logger.info("Model ready: %s | labels: %s", name, sorted(set(id2label_norm.values())))


def split_into_sentences(text: str) -> List[Dict]:
    """Split text into sentences and return with character positions."""
    sentences_with_positions = []
    current_pos = 0
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)
    for sentence in sentences:
        if sentence.strip():
            start_pos = text.find(sentence, current_pos)
            end_pos = start_pos + len(sentence)
            sentences_with_positions.append({'text': sentence, 'start': start_pos, 'end': end_pos})
            current_pos = end_pos
    return sentences_with_positions


def analyze_sentiment_sentence(sentence: str) -> Dict[str, float]:
    """Return normalized confidence scores for a single sentence."""
    # Prefer pipeline for consistency with model config labels
    scores_norm: Dict[str, float] = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    if hf_pipeline is None:
        raise RuntimeError("Model pipeline not initialized")
    results = hf_pipeline(sentence, return_all_scores=True, truncation=True)
    # HF returns list of list when batching; normalize to inner list
    if results and isinstance(results, list) and isinstance(results[0], dict):
        results = [results]
    for item in results[0]:
        lbl = _norm_label(item.get("label"))
        scores_norm[lbl] = float(item.get("score", 0.0))
    # Ensure all keys exist
    for k in ("positive", "negative", "neutral"):
        scores_norm.setdefault(k, 0.0)
    return scores_norm


def get_highlight_color(sentiment_class: str, scores: Dict[str, float]) -> Optional[str]:
    """Get color based on sentiment and confidence score."""
    if sentiment_class == 'neutral':
        return None  # Skip neutral sentences
    if sentiment_class == 'positive':
        base_lightness = 255 - int(scores['positive'] * 155)
        return f'rgb({base_lightness}, 255, {base_lightness})'
    elif sentiment_class == 'negative':
        base_lightness = 255 - int(scores['negative'] * 155)
        return f'rgb(255, {base_lightness}, {base_lightness})'
    return None


def highlight_html(html_content: str, sentiment_results: List[Dict]) -> str:
    """Apply sentiment highlighting to HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    html_str = str(soup)
    sentiments_sorted = sorted(sentiment_results, key=lambda x: x['position']['start'], reverse=True)
    for sentiment in sentiments_sorted:
        color = get_highlight_color(sentiment['class'], sentiment['confidence_scores'])
        if color:
            sentence = sentiment['sentence']
            highlighted = f'<span style="background-color: {color};">{sentence}</span>'
            html_str = html_str.replace(sentence, highlighted, 1)
    return html_str


# --------------------
# Startup
# --------------------
@app.on_event("startup")
async def load_model_on_startup():
    """Load default FinBERT model on startup (if torch is available)."""
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch not available — FinBERT will be disabled until torch is installed.")
        return
    try:
        _load_model(ACTIVE_MODEL_NAME or "ProsusAI/finbert")
    except Exception as e:
        logger.error("Failed to load FinBERT on startup: %s", e, exc_info=True)


# --------------------
# Basic routes
# --------------------
@app.get("/")
async def root():
    return {
        "message": "Sentiment Analysis Service",
        "active_model": ACTIVE_MODEL_NAME,
        "torch_available": TORCH_AVAILABLE,
        "endpoints": {
            "POST /analyze": "Analyze sentiment of text and optionally highlight HTML",
            "GET /health": "Health check",
            "GET /models": "List available/active models",
            "POST /models/activate": "Activate a BERT model",
            "POST /models/from_hf": "Add a BERT model from Hugging Face"
        }
    }


@app.get("/health")
async def health_check():
    model_loaded = (model is not None) and (tokenizer is not None) and (hf_pipeline is not None)
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "service": "sentiment-analysis",
        "model_loaded": model_loaded,
        "active_model": ACTIVE_MODEL_NAME,
        "torch_available": TORCH_AVAILABLE
    }


# --------------------
# Model management (to match your UI)
# --------------------
@app.get("/models")
async def get_models():
    # spaCy stub so your UI can render the dropdown (no spaCy in this service)
    spacy_stub = {
        "available": ["en_core_web_sm", "en_core_web_lg"],  # en_core_web_trf intentionally omitted
        "active": None
    }
    bert_info = {
        "available": sorted(list(BERT_CATALOG)),
        "active": ACTIVE_MODEL_NAME if (model is not None and tokenizer is not None) else None,
        "torch_available": TORCH_AVAILABLE
    }
    return JSONResponse({"spacy": spacy_stub, "bert": bert_info})


@app.post("/models/activate")
async def activate_model(req: ActivateRequest):
    if not TORCH_AVAILABLE:
        raise HTTPException(status_code=503, detail="PyTorch is not available in this Python environment.")
    name = (req.name or "").strip() or (ACTIVE_MODEL_NAME or "ProsusAI/finbert")
    try:
        _load_model(name)
        if name not in BERT_CATALOG:
            BERT_CATALOG.append(name)
        return JSONResponse({"status": "success", "active": ACTIVE_MODEL_NAME, "bert": {"available": sorted(BERT_CATALOG)}})
    except Exception as e:
        logger.error("Activation failed for %s: %s", name, e, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to activate model '{name}': {e}")


@app.post("/models/from_hf")
async def add_from_hf(req: HFRequest):
    if not TORCH_AVAILABLE:
        raise HTTPException(status_code=503, detail="PyTorch is not available in this Python environment.")
    repo = (req.repo or "").strip()
    if not repo:
        raise HTTPException(status_code=400, detail="Missing repo.")
    try:
        # quick validation: try to load and then discard
        _tok = AutoTokenizer.from_pretrained(repo)
        _mdl = AutoModelForSequenceClassification.from_pretrained(repo)
        if repo not in BERT_CATALOG:
            BERT_CATALOG.append(repo)
        return JSONResponse({"status": "success", "name": repo, "available": sorted(BERT_CATALOG)})
    except Exception as e:
        logger.error("Failed to add HF repo %s: %s", repo, e, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Could not load from HF repo '{repo}': {e}")


# --------------------
# Sentiment analysis
# --------------------
@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment_endpoint(request: SentimentRequest):
    """
    Analyze sentiment of provided text and optionally highlight HTML.
    """
    if not (model and tokenizer and hf_pipeline):
        raise HTTPException(
            status_code=503,
            detail="Model not loaded (or torch unavailable). Activate a model via /models/activate or wait for service to initialize."
        )

    try:
        sentences = split_into_sentences(request.text)
        if not sentences:
            raise HTTPException(status_code=400, detail="No sentences found in the provided text.")

        results = []
        for sentence_data in sentences:
            scores = analyze_sentiment_sentence(sentence_data['text'])
            # classification by max score
            sentiment_class = max(scores, key=scores.get)
            results.append({
                "sentence": sentence_data['text'],
                "class": sentiment_class,
                "position": {"start": sentence_data['start'], "end": sentence_data['end']},
                "confidence_scores": scores
            })

        highlighted_html = None
        if request.html:
            highlighted_html = highlight_html(request.html, results)

        return SentimentResponse(sentiment_results=results, highlighted_html=highlighted_html)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")