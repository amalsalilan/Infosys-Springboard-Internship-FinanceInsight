#ner_service.py


from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import os
import logging
import sys
import warnings
from pathlib import Path

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
        logging.FileHandler('logs/ner_service.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial NER Service",
    description="API for Named Entity Recognition in financial documents",
    version="1.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", "http://127.0.0.1:8080",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Global state
# --------------------
ner_pipeline = None
ACTIVE_NER_MODEL = os.getenv("NER_MODEL", "dslim/bert-base-NER")

# A small catalog of NER models to choose from (dedup + sorted)
DEFAULT_NER_CHOICES = list({ACTIVE_NER_MODEL, "dbmdz/bert-large-cased-finetuned-conll03-english"})
NER_CATALOG: List[str] = sorted(DEFAULT_NER_CHOICES)

def _device_index() -> int:
    return 0 if TORCH_AVAILABLE and torch.cuda.is_available() else -1  # type: ignore


class NERRequest(BaseModel):
    """Request model for NER"""
    text: str


class Entity(BaseModel):
    """Entity model"""
    entity: str
    word: str
    start: int
    end: int
    score: float


class NERResponse(BaseModel):
    """Response model for NER"""
    entities: List[Dict]
    highlighted_html: Optional[str] = None


def load_ner_model(name: str):
    """Create/update the global NER pipeline."""
    global ner_pipeline, ACTIVE_NER_MODEL
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is not available in this Python environment.")
    logger.info("Loading tokenizer for NER: %s", name)
    tokenizer = AutoTokenizer.from_pretrained(name)
    logger.info("Loading model for NER: %s", name)
    model = AutoModelForTokenClassification.from_pretrained(name)
    logger.info("Creating NER pipeline...")
    ner_pipeline_local = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
        device=_device_index(),
    )
    ner_pipeline = ner_pipeline_local
    ACTIVE_NER_MODEL = name
    logger.info("NER model ready: %s", name)


@app.on_event("startup")
async def load_model():
    """Load NER model on startup (if torch is available)"""
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch not available — NER will be disabled until torch is installed.")
        return
    logger.info(f"Starting NER model loading from {ACTIVE_NER_MODEL}...")
    try:
        load_ner_model(ACTIVE_NER_MODEL)
    except Exception as e:
        logger.error(f"Failed to load NER model: {str(e)}", exc_info=True)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Financial NER Service",
        "model": ACTIVE_NER_MODEL,
        "torch_available": TORCH_AVAILABLE,
        "endpoints": {
            "POST /recognize": "Recognize financial entities in text",
            "GET /health": "Health check endpoint",
            "GET /models": "List available/active NER models",
            "POST /models/activate": "Activate a NER model",
            "POST /models/from_hf": "Validate and register a HF NER model (no activation)",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = ner_pipeline is not None
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "service": "financial-ner",
        "model_loaded": model_loaded,
        "active_model": ACTIVE_NER_MODEL,
        "torch_available": TORCH_AVAILABLE
    }


def get_entity_color(entity_type: str) -> str:
    """Get color based on entity type"""
    colors = {
        "PER": "#FFB6C1",      # Person - Light Pink
        "ORG": "#ADD8E6",      # Organization - Light Blue
        "LOC": "#90EE90",      # Location - Light Green
        "MISC": "#FFE4B5",     # Miscellaneous - Moccasin
        "CARDINAL": "#DDA0DD", # Numbers - Plum
        "DATE": "#F0E68C",     # Date - Khaki
        "MONEY": "#98FB98",    # Money - Pale Green
        "PERCENT": "#FFDAB9",  # Percent - Peach Puff
    }
    base_entity = entity_type.replace("B-", "").replace("I-", "")
    return colors.get(base_entity, "#E0E0E0")  # Default gray


def highlight_entities_in_html(text: str, entities: List[Dict]) -> str:
    """
    Highlight entities in HTML
    """
    sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)
    highlighted_text = text

    for entity in sorted_entities:
        start = entity['start']
        end = entity['end']
        entity_text = entity['word']
        entity_type = entity['entity_group']
        score = entity['score']
        color = get_entity_color(entity_type)

        highlighted = (
            f'<span style="background-color: {color}; padding: 2px 6px; '
            f'border-radius: 3px; margin: 0 2px; display: inline-block;" '
            f'title="Confidence: {score:.2f}">{entity_text} '
            f'<sup style="font-size: 0.65em; font-weight: bold; opacity: 0.8;">[{entity_type}]</sup></span>'
        )
        highlighted_text = highlighted_text[:start] + highlighted + highlighted_text[end:]

    html_output = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NER Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.8;
        }}
        .content {{
            padding: 20px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="content">
        {highlighted_text}
    </div>
</body>
</html>"""
    return html_output


@app.get("/models")
async def get_models():
    """List available and active NER models (for UI Model Settings)"""
    return JSONResponse({
        "ner": {
            "available": sorted(NER_CATALOG),
            "active": ACTIVE_NER_MODEL if ner_pipeline is not None else None,
            "torch_available": TORCH_AVAILABLE
        }
    })


class ActivateRequest(BaseModel):
    name: Optional[str] = None


class HFRequest(BaseModel):
    repo: str


@app.post("/models/activate")
async def activate_model(req: ActivateRequest):
    """Activate a selected NER model"""
    if not TORCH_AVAILABLE:
        raise HTTPException(status_code=503, detail="PyTorch is not available in this Python environment.")
    name = (req.name or "").strip() or ACTIVE_NER_MODEL
    try:
        load_ner_model(name)
        if name not in NER_CATALOG:
            NER_CATALOG.append(name)
        return JSONResponse({"status": "success", "active": ACTIVE_NER_MODEL, "available": sorted(NER_CATALOG)})
    except Exception as e:
        logger.error("Activation failed for %s: %s", name, e, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to activate model '{name}': {e}")


@app.post("/models/from_hf")
async def add_from_hf(req: HFRequest):
    """Validate and register a HF NER model without activating it"""
    if not TORCH_AVAILABLE:
        raise HTTPException(status_code=503, detail="PyTorch is not available in this Python environment.")
    repo = (req.repo or "").strip()
    if not repo:
        raise HTTPException(status_code=400, detail="Missing repo.")
    try:
        # Validate by loading once; errors bubble if invalid
        _tok = AutoTokenizer.from_pretrained(repo)
        _mdl = AutoModelForTokenClassification.from_pretrained(repo)
        if repo not in NER_CATALOG:
            NER_CATALOG.append(repo)
        return JSONResponse({"status": "success", "name": repo, "available": sorted(NER_CATALOG)})
    except Exception as e:
        logger.error("Failed to add HF repo %s: %s", repo, e, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Could not load from HF repo '{repo}': {e}")


@app.post("/recognize")
async def recognize_entities(request: NERRequest):
    """
    Recognize named entities in text
    """
    logger.info(f"Received NER request for text of length {len(request.text)}")

    if not ner_pipeline:
        logger.error("NER model not loaded yet")
        msg = "NER model not loaded. Please wait for service to initialize."
        if not TORCH_AVAILABLE:
            msg += " PyTorch is not installed; install torch (or run with Python 3.11/3.12)."
        raise HTTPException(status_code=503, detail=msg)

    try:
        # Run NER
        logger.info("Running NER pipeline...")
        entities = ner_pipeline(request.text)
        logger.info(f"Found {len(entities)} entities")

        # Convert numpy float32 to Python float for JSON serialization
        entities_json = []
        for entity in entities:
            entities_json.append({
                "entity_group": entity["entity_group"],
                "score": float(entity["score"]),
                "word": entity["word"],
                "start": int(entity["start"]),
                "end": int(entity["end"])
            })
        logger.debug(f"Converted {len(entities_json)} entities to JSON format")

        # Generate highlighted HTML
        logger.info("Generating highlighted HTML...")
        highlighted_html = highlight_entities_in_html(request.text, entities)

        # Save HTML to output folder
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        html_file = os.path.join(output_dir, "ner_results.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(highlighted_html)
        logger.info(f"Saved NER results to {html_file}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "entities": entities_json,
                "highlighted_html": highlighted_html,
                "saved_file": html_file
            }
        )

    except Exception as e:
        logger.error(f"Error during NER: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during NER: {str(e)}"
        )


@app.get("/visualization")
async def get_visualization():
    """
    Get the latest HTML visualization
    """
    html_file = os.path.join("output", "ner_results.html")

    if not os.path.exists(html_file):
        raise HTTPException(
            status_code=404,
            detail="No visualization found. Run NER first."
        )

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)