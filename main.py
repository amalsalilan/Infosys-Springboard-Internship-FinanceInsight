import re
import os
import json
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

import fitz  # PyMuPDF

# Try to make torch optional so the server can run on Python 3.13 even if torch wheels are unavailable
try:
    import torch  # type: ignore
    TORCH_AVAILABLE = True
except Exception as _e:
    torch = None  # type: ignore
    TORCH_AVAILABLE = False

from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    AutoModelForSequenceClassification,
    pipeline,
)

# NEW
import tarfile
import zipfile
from pydantic import BaseModel

# Load env
from dotenv import load_dotenv, find_dotenv
ENV_PATH = find_dotenv()
load_dotenv(ENV_PATH)

# Try to import docling (for text extraction convenience only)
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DocumentConverter = None
    DOCLING_AVAILABLE = False

# Try to import langextract
try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except Exception:
    lx = None
    LANGEXTRACT_AVAILABLE = False

# Try to import spaCy + displaCy
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
    SPACY_MODEL_NAME = os.getenv("SPACY_MODEL", "en_core_web_sm")
    try:
        SPACY_NLP = spacy.load(SPACY_MODEL_NAME)
        try:
            SPACY_LABELS = set(SPACY_NLP.get_pipe("ner").labels)
        except Exception:
            SPACY_LABELS = set()
    except Exception:
        SPACY_AVAILABLE = False
        SPACY_NLP = None
        SPACY_LABELS = set()
except Exception:
    spacy = None
    displacy = None
    SPACY_AVAILABLE = False
    SPACY_NLP = None
    SPACY_LABELS = set()
    SPACY_MODEL_NAME = os.getenv("SPACY_MODEL", "en_core_web_sm")

# Optional auth import
try:
    from auth import router as auth_router, get_current_user
    from database import User  # noqa
except Exception:
    auth_router = None
    get_current_user = None
    User = None

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finance-ner-backend")

app = FastAPI(title="Finance Insight NER Tool")

if auth_router:
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NEW: Model store and catalog
MODELS_DIR = Path(os.getenv("MODELS_DIR", "./models_store")).resolve()
SPACY_MODELS_PATH = MODELS_DIR / "spacy"
BERT_MODELS_PATH = MODELS_DIR / "bert"
CATALOG_FILE = MODELS_DIR / "catalog.json"
SPACY_MODELS_PATH.mkdir(parents=True, exist_ok=True)
BERT_MODELS_PATH.mkdir(parents=True, exist_ok=True)

def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-\.\/]+", "-", s.strip())
    return re.sub(r"-{2,}", "-", s).strip("-").lower() or f"model-{uuid4().hex[:8]}"

def _unique_name(base_dir: Path, base_name: str) -> str:
    name = _slug(base_name)
    candidate = name
    i = 1
    while (base_dir / candidate).exists():
        candidate = f"{name}-{i}"
        i += 1
    return candidate

def _safe_extract_tar(tar: tarfile.TarFile, path: Path):
    path = path.resolve()
    for member in tar.getmembers():
        member_path = (path / member.name).resolve()
        if not str(member_path).startswith(str(path)):
            raise RuntimeError("Unsafe tar archive (path traversal)")
    tar.extractall(path)

def _safe_extract_zip(zf: zipfile.ZipFile, path: Path):
    path = path.resolve()
    for member in zf.infolist():
        member_path = (path / member.filename).resolve()
        if not str(member_path).startswith(str(path)):
            raise RuntimeError("Unsafe zip archive (path traversal)")
    zf.extractall(path)

def _find_dir_with_file(root: Path, filename: str) -> Optional[Path]:
    for p, _, files in os.walk(root):
        if filename in files:
            return Path(p)
    return None

def _load_catalog() -> Dict[str, Any]:
    if CATALOG_FILE.exists():
        try:
            with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "spacy_extra": [],          # any non-local names to persist
        "bert_hf": [],              # HF repo names persisted
        "active": {
            "spacy": None,
            "bert": None,
        }
    }

def _save_catalog(cat: Dict[str, Any]):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CATALOG_FILE, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2)
    except Exception as e:
        logger.warning("Failed to save catalog: %s", e)

CATALOG = _load_catalog()

# Built-in choices we always expose in the dropdowns
DEFAULT_SPACY_CHOICES = ["en_core_web_sm", "en_core_web_lg", "en_core_web_trf"]
DEFAULT_BERT_CHOICES  = [os.getenv("FINBERT_MODEL", "ProsusAI/finbert"), "yiyanghkust/finbert-tone"]

def _list_spacy_available() -> List[str]:
    names = set([p.name for p in SPACY_MODELS_PATH.iterdir() if p.is_dir()])
    for n in CATALOG.get("spacy_extra", []):
        names.add(n)
    # include default env name and built-ins
    if SPACY_MODEL_NAME:
        names.add(SPACY_MODEL_NAME)
    names.update(DEFAULT_SPACY_CHOICES)
    return sorted(names)

def _list_bert_available() -> List[str]:
    names = set([p.name for p in BERT_MODELS_PATH.iterdir() if p.is_dir()])
    for n in CATALOG.get("bert_hf", []):
        names.add(n)
    # include default env name and built-ins
    fin_default = os.getenv("FINBERT_MODEL", "ProsusAI/finbert")
    if fin_default:
        names.add(fin_default)
    names.update(DEFAULT_BERT_CHOICES)
    return sorted(names)

# Device selection (works even when torch isn't installed)
device = 0 if TORCH_AVAILABLE and torch.cuda.is_available() else -1

# === Load BERT NER once (legacy) — optional ===
NER_MODEL_NAME = "dslim/bert-base-NER"
gen_ner_pipeline = None
if TORCH_AVAILABLE:
    try:
        _tok = AutoTokenizer.from_pretrained(NER_MODEL_NAME)
        _mdl = AutoModelForTokenClassification.from_pretrained(NER_MODEL_NAME)
        gen_ner_pipeline = pipeline(
            "ner",
            model=_mdl,
            tokenizer=_tok,
            aggregation_strategy="simple",
            device=device,
        )
    except Exception as e:
        logger.warning("Could not load general NER model '%s': %s", NER_MODEL_NAME, e)
else:
    logger.info("PyTorch not available — disabling general NER pipeline initialization.")

# === Load FinBERT (sentiment) — optional ===
FINBERT_MODEL_NAME = os.getenv("FINBERT_MODEL", "ProsusAI/finbert")
FINBERT_READY = False
finbert_pipeline = None
if TORCH_AVAILABLE:
    try:
        finbert_tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL_NAME)
        finbert_model = AutoModelForSequenceClassification.from_pretrained(FINBERT_MODEL_NAME)
        finbert_pipeline = pipeline(
            "text-classification",
            model=finbert_model,
            tokenizer=finbert_tokenizer,
            device=device,
            truncation=True,
        )
        FINBERT_READY = True
    except Exception as e:
        logger.warning("Could not load FinBERT (%s). Sentiment will be unavailable. Error: %s", FINBERT_MODEL_NAME, e)
else:
    logger.warning("PyTorch not available — FinBERT is disabled on this runtime.")

converter = DocumentConverter() if DOCLING_AVAILABLE else None

# Colors for spaCy displaCy
SPACY_COLORS = {
    "PERSON": "#a3e635",
    "ORG": "#60a5fa",
    "GPE": "#f59e0b",
    "LOC": "#fca5a5",
    "NORP": "#a78bfa",
    "PRODUCT": "#34d399",
    "EVENT": "#f472b6",
    "WORK_OF_ART": "#93c5fd",
    "LAW": "#ef4444",
    "LANGUAGE": "#14b8a6",
    "DATE": "#38bdf8",
    "TIME": "#67e8f9",
    "PERCENT": "#9ca3af",
    "MONEY": "#facc15",
    "QUANTITY": "#fbcfe8",
    "ORDINAL": "#cbd5e1",
    "CARDINAL": "#e5e7eb",
    "FAC": "#f97316",
}
SPACY_COLORS.update({
    "STOCK_PRICE": "#facc15",
    "REVENUE": "#34d399",
    "EARNINGS": "#fb923c",
    "FINANCIAL_RATIO": "#c084fc",
    "FINANCIAL_DATE": "#38bdf8",
    "MARKET_EVENT": "#f472b6",
    "PERFORMANCE_METRIC": "#9b59b6",
})
CUSTOM_FIN_LABELS = {
    "STOCK_PRICE", "REVENUE", "EARNINGS", "FINANCIAL_RATIO",
    "FINANCIAL_DATE", "MARKET_EVENT", "PERFORMANCE_METRIC",
}
SPACY_GROUP_MAP = {
    "ORG": ["ORG"],
    "PERSON": ["PERSON"],
    "LOC": ["LOC", "GPE", "FAC"],
    "FINANCIAL_DATE": ["DATE", "TIME"],
    "MARKET_EVENT": ["EVENT"],
    "FINANCIAL_RATIO": ["PERCENT"],
}

# Financial regex patterns
FIN_PATTERNS = [
    (r"\$?\d{1,3}(?:[,\d]{0,})(?:\.\d{1,2})?\s?(?:USD|usd|dollars|m|b|million|billion|k|thousand)?", "STOCK_PRICE"),
    (r"(?:\d+\s)?(?:million|billion|trillion)\s(?:dollars|USD|€|£|¥)", "STOCK_PRICE"),
    (r"(?:revenue|sales|income|turnover|net sales|total revenue)\s*[:=]?\s*\$?\d{1,3}(?:[,\d]{0,})(?:\.\d{1,2})?\s*(?:million|billion|M|B|USD)?", "REVENUE"),
    (r"(?:Q[1-4]\s*\d{4}\s(?:revenue|sales)|FY\s?\d{4}\s(?:revenue|sales))", "REVENUE"),
    (r"(EPS|earnings per share|net profit|quarterly earnings|profit after tax|EBITDA|operating income|net income)\s*[:=]?\s*\$?\d{1,3}(?:[,\d]{0,})(?:\.\d{1,2})?\s*(?:million|billion|M|B|USD)?", "EARNINGS"),
    (r"(P/E\s*ratio|debt-to-equity|ROI|ROE|profit margin|gross margin|operating margin|liquidity ratio|current ratio|quick ratio|debt ratio)", "FINANCIAL_RATIO"),
    (r"\d+\.?\d*%", "FINANCIAL_RATIO"),
    (r"(Q[1-4]\s*\d{4}|FY\s?\d{4}|fiscal year\s*\d{4}|\d{1,2}(?:st|nd|rd|th)?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:\s\d{4})?|\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})", "FINANCIAL_DATE"),
    (r"(IPO|acquisition|merger|dividend|buyback|stock split|tender offer|takeover|spin-off|bond issuance|debt offering)", "MARKET_EVENT"),
    (r"(growth\s\d+%|operating margin|EBITDA|revenue growth|net income margin|CAGR|market capitalization)", "PERFORMANCE_METRIC"),
    (r"\b(?:S&P\s*500|Dow\s*Jones|NASDAQ|FTSE\s*100|Nikkei\s*225)\b", "MARKET_EVENT"),
]

def run_regex_on_text(text: str) -> List[Dict[str, Any]]:
    ents: List[Dict[str, Any]] = []
    for pattern, label in FIN_PATTERNS:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            start, end = m.start(), m.end()
            word = m.group().strip()
            if not word:
                continue
            overlap_idx = None
            for i, ex in enumerate(ents):
                if max(start, ex["start"]) < min(end, ex["end"]):
                    overlap_idx = i
                    break
            if overlap_idx is not None:
                existing = ents[overlap_idx]
                if (end - start) > (existing["end"] - existing["start"]):
                    ents[overlap_idx] = {"start": start, "end": end, "label": label, "word": word}
            else:
                ents.append({"start": start, "end": end, "label": label, "word": word})
    return ents

def build_page_token_stream(page) -> Dict[str, Any]:
    raw_words = page.get_text("words")
    raw_words.sort(key=lambda w: (round(w[1], 1), w[0]))
    tokens = []
    char_pos = 0
    for w in raw_words:
        x0, y0, x1, y1, word_text = w[0], w[1], w[2], w[3], w[4]
        if not word_text:
            continue
        start = char_pos
        char_pos += len(word_text)
        end = char_pos
        tokens.append({"text": word_text, "start": start, "end": end, "bbox": (x0, y0, x1, y1)})
        char_pos += 1
    page_text = " ".join([t["text"] for t in tokens])
    cur = 0
    for t in tokens:
        t_start = cur
        t_end = cur + len(t["text"])
        t["start"] = t_start
        t["end"] = t_end
        cur = t_end + 1
    return {
        "page_text": page_text,
        "tokens": tokens,
        "page_width": page.rect.width,
        "page_height": page.rect.height,
    }

# Determine get_current_user dependency
if get_current_user:
    get_current_user_dep = get_current_user
else:
    async def _noop_current_user():
        return None
    get_current_user_dep = _noop_current_user

# ---- LangExtract helpers (unchanged) ----
def _parse_langextract_examples(examples_str: Optional[str]) -> List[Any]:
    if not examples_str or not examples_str.strip() or not LANGEXTRACT_AVAILABLE:
        return []
    try:
        parsed = json.loads(examples_str)
    except Exception as e:
        logging.warning("Failed to parse 'examples' as JSON: %s", e)
        return []
    if isinstance(parsed, dict):
        parsed = [parsed]
    ex_objs = []
    try:
        for ex in parsed:
            text = ex.get("text", "")
            extractions = []
            for e in ex.get("extractions", []):
                extraction_class = e.get("extraction_class") or e.get("class") or e.get("label") or "entity"
                extraction_text = e.get("extraction_text") or e.get("text") or ""
                attributes = e.get("attributes", {})
                extractions.append(
                    lx.data.Extraction(
                        extraction_class=extraction_class,
                        extraction_text=extraction_text,
                        attributes=attributes,
                    )
                )
            ex_objs.append(lx.data.ExampleData(text=text, extractions=extractions))
    except Exception as e:
        logging.warning("Error constructing ExampleData: %s", e)
        return []
    return ex_objs

def _flatten_langextract_entities(result_obj: Any) -> List[Dict[str, Any]]:
    entities: List[Dict[str, Any]] = []
    try:
        docs = getattr(result_obj, "annotated_documents", None) or []
        for d in docs:
            for ent in getattr(d, "extractions", []) or []:
                entities.append(
                    {
                        "text": getattr(ent, "extraction_text", ""),
                        "label": getattr(ent, "extraction_class", "ENTITY"),
                        "attributes": getattr(ent, "attributes", {}),
                        "page": "-",
                    }
                )
    except Exception as e:
        logging.warning("Could not flatten LangExtract entities: %s", e)
    return entities

# ---- spaCy helpers for manual rendering ----
def _compute_spacy_and_custom_filters(entity_types: Optional[str], spacy_labels_available: set):
    if not entity_types or entity_types == "all":
        return None, None
    try:
        requested = [s.strip().upper() for s in json.loads(entity_types)]
    except Exception:
        return None, None
    spacy_filter = set()
    custom_filter = set()
    for r in requested:
        if r in spacy_labels_available:
            spacy_filter.add(r)
        if r in SPACY_GROUP_MAP:
            spacy_filter.update(SPACY_GROUP_MAP[r])
        if r in CUSTOM_FIN_LABELS:
            custom_filter.add(r)
    spacy_filter = {l for l in spacy_filter if l in spacy_labels_available}
    return (spacy_filter if len(spacy_filter) > 0 else set()), (custom_filter if len(custom_filter) > 0 else set())

def _add_non_overlapping_span(acc: List[Dict[str, Any]], start: int, end: int, label: str):
    if start is None or end is None or start >= end:
        return
    for i, ex in enumerate(acc):
        if max(start, ex["start"]) < min(end, ex["end"]):
            if (end - start) > (ex["end"] - ex["start"]):
                acc[i] = {"start": start, "end": end, "label": label}
            return
    acc.append({"start": start, "end": end, "label": label})

# ---- FinBERT helpers ----
_SENT_SPLIT_RE = re.compile(r"[^.!?;\n]+[.!?;\n]+|[^.!?;\n]+$", re.MULTILINE)

def _sentence_spans(text: str) -> List[Tuple[int, int]]:
    spans = [(m.start(), m.end()) for m in _SENT_SPLIT_RE.finditer(text or "")]
    return spans if spans else ([(0, len(text))] if text else [])

def _norm_sent_label(label: str) -> str:
    l = (label or "").upper()
    if "POS" in l:
        return "POSITIVE"
    if "NEG" in l:
        return "NEGATIVE"
    if "NEU" in l:
        return "NEUTRAL"
    return l

# =========================
# NEW: Model management helpers
# =========================
spacy_cache: Dict[str, Any] = {}
bert_cache: Dict[str, Any] = {}

def activate_spacy_model(name: Optional[str]) -> Tuple[bool, str]:
    global SPACY_NLP, SPACY_AVAILABLE, SPACY_LABELS, SPACY_MODEL_NAME, CATALOG
    if spacy is None:
        return False, "spaCy not installed on server."
    target = name or os.getenv("SPACY_MODEL", "en_core_web_sm")
    path = SPACY_MODELS_PATH / target
    try:
        if path.exists():
            nlp = spacy.load(str(path))
        else:
            # Try as installed package name (e.g., en_core_web_md/lg/trf)
            nlp = spacy.load(target)
        SPACY_NLP = nlp
        SPACY_AVAILABLE = True
        try:
            SPACY_LABELS = set(nlp.get_pipe("ner").labels)
        except Exception:
            SPACY_LABELS = set()
        SPACY_MODEL_NAME = target
        spacy_cache[target] = nlp
        # persist active
        CATALOG["active"]["spacy"] = target
        if target not in CATALOG.get("spacy_extra", []):
            # store non-local names so they show up after restart
            if not (SPACY_MODELS_PATH / target).exists():
                CATALOG["spacy_extra"].append(target)
        _save_catalog(CATALOG)
        logger.info("Activated spaCy model: %s", target)
        return True, target
    except Exception as e:
        logger.exception("Failed to activate spaCy model %s", target)
        return False, f"Failed to load spaCy model '{target}': {e}"

def activate_bert_model(name: Optional[str]) -> Tuple[bool, str]:
    global finbert_pipeline, FINBERT_READY, FINBERT_MODEL_NAME, CATALOG
    if not TORCH_AVAILABLE:
        return False, "PyTorch is not available in this Python environment. Install torch (or run on Python 3.11/3.12) to enable BERT/FinBERT."
    target = name or os.getenv("FINBERT_MODEL", "ProsusAI/finbert")
    path = BERT_MODELS_PATH / target
    try:
        # Use cache if available
        if target in bert_cache:
            finbert_pipeline = bert_cache[target]
            FINBERT_MODEL_NAME = target
            FINBERT_READY = True
        else:
            load_from = str(path) if path.exists() else target
            tok = AutoTokenizer.from_pretrained(load_from)
            mdl = AutoModelForSequenceClassification.from_pretrained(load_from)
            pl = pipeline(
                "text-classification",
                model=mdl,
                tokenizer=tok,
                device=device,
                truncation=True,
            )
            finbert_pipeline = pl
            FINBERT_MODEL_NAME = target
            FINBERT_READY = True
            bert_cache[target] = pl
        # persist active + HF repo registration
        CATALOG["active"]["bert"] = target
        if not (BERT_MODELS_PATH / target).exists():
            if target not in CATALOG.get("bert_hf", []):
                CATALOG.setdefault("bert_hf", []).append(target)
        _save_catalog(CATALOG)
        logger.info("Activated BERT model: %s", target)
        return True, target
    except Exception as e:
        logger.exception("Failed to activate BERT model %s", target)
        FINBERT_READY = False
        return False, f"Failed to load BERT/FinBERT model '{target}': {e}"

def _scan_models_response() -> Dict[str, Any]:
    return {
        "spacy": {
            "available": _list_spacy_available(),
            "active": CATALOG.get("active", {}).get("spacy") or SPACY_MODEL_NAME if SPACY_AVAILABLE else None,
        },
        "bert": {
            "available": _list_bert_available(),
            "active": CATALOG.get("active", {}).get("bert") or (FINBERT_MODEL_NAME if FINBERT_READY else None),
            "torch_available": TORCH_AVAILABLE,
        },
    }

# =========================
# NEW: Model management routes
# =========================
class ActivateRequest(BaseModel):
    type: str
    name: Optional[str] = None

class HFRequest(BaseModel):
    repo: str

@app.get("/models")
async def get_models(current_user=Depends(get_current_user_dep)):
    try:
        return JSONResponse(_scan_models_response())
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/models/activate")
async def post_activate_model(req: ActivateRequest, current_user=Depends(get_current_user_dep)):
    t = (req.type or "").strip().lower()
    if t not in ("spacy", "bert"):
        return JSONResponse({"status": "error", "message": "Invalid type. Use 'spacy' or 'bert'."}, status_code=400)
    if t == "spacy":
        ok, msg = activate_spacy_model(req.name)
    else:
        ok, msg = activate_bert_model(req.name)
    if not ok:
        return JSONResponse({"status": "error", "message": msg}, status_code=400)
    return JSONResponse({"status": "success", "message": f"Activated {t} model '{msg}'", **_scan_models_response()})

@app.post("/models/spacy/upload")
async def upload_spacy_model(file: UploadFile = File(...), current_user=Depends(get_current_user_dep)):
    # Accepts .zip/.tar/.tar.gz containing a spaCy pipeline directory (with meta.json)
    tmp_dir = Path(tempfile.mkdtemp(prefix="spacy_up_"))
    tmp_file = tmp_dir / (file.filename or f"spacy_{uuid4().hex}")
    try:
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(file.file, f)

        extract_dir = tmp_dir / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        name_lower = (file.filename or "").lower()
        try:
            if name_lower.endswith((".tar.gz", ".tgz", ".tar")):
                with tarfile.open(tmp_file, "r:*") as tf:
                    _safe_extract_tar(tf, extract_dir)
            elif name_lower.endswith(".zip"):
                with zipfile.ZipFile(tmp_file, "r") as zf:
                    _safe_extract_zip(zf, extract_dir)
            else:
                # Try tar first fallback to zip
                try:
                    with tarfile.open(tmp_file, "r:*") as tf:
                        _safe_extract_tar(tf, extract_dir)
                except Exception:
                    with zipfile.ZipFile(tmp_file, "r") as zf:
                        _safe_extract_zip(zf, extract_dir)
        except Exception as e:
            return JSONResponse({"status": "error", "message": f"Failed to extract archive: {e}"}, status_code=400)

        pipeline_dir = _find_dir_with_file(extract_dir, "meta.json") or extract_dir
        meta_path = pipeline_dir / "meta.json"
        if not meta_path.exists():
            # Try "config.cfg" as a fallback
            if not (pipeline_dir / "config.cfg").exists():
                return JSONResponse({"status": "error", "message": "No spaCy pipeline found (meta.json/config.cfg missing)."}, status_code=400)

        model_name = None
        try:
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    model_name = meta.get("name") or meta.get("project", None)
        except Exception:
            pass
        if not model_name:
            # name from archive
            model_name = Path(file.filename or f"spacy_{uuid4().hex}").stem

        model_name = _unique_name(SPACY_MODELS_PATH, model_name)
        dest = SPACY_MODELS_PATH / model_name
        shutil.move(str(pipeline_dir), str(dest))

        # Refresh catalog
        if model_name not in CATALOG.get("spacy_extra", []):
            # local model lives under spacy folder; no need to add to extra
            pass
        _save_catalog(CATALOG)

        # Optionally activate immediately? Frontend calls activate after upload; we won't auto-activate.
        return JSONResponse({"status": "success", "name": model_name})
    except Exception as e:
        logger.exception("spaCy upload failed")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    finally:
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

@app.post("/models/bert/upload")
async def upload_bert_model(file: UploadFile = File(...), current_user=Depends(get_current_user_dep)):
    if not TORCH_AVAILABLE:
        return JSONResponse({"status": "error", "message": "PyTorch is not available in this Python environment. Install torch to upload/activate BERT models."}, status_code=400)

    # Accepts .zip/.tar/.tar.gz of a HF Transformers SequenceClassification model folder (config.json, tokenizer files, model weights)
    tmp_dir = Path(tempfile.mkdtemp(prefix="bert_up_"))
    tmp_file = tmp_dir / (file.filename or f"bert_{uuid4().hex}")
    try:
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(file.file, f)

        extract_dir = tmp_dir / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        name_lower = (file.filename or "").lower()
        try:
            if name_lower.endswith((".tar.gz", ".tgz", ".tar")):
                with tarfile.open(tmp_file, "r:*") as tf:
                    _safe_extract_tar(tf, extract_dir)
            elif name_lower.endswith(".zip"):
                with zipfile.ZipFile(tmp_file, "r") as zf:
                    _safe_extract_zip(zf, extract_dir)
            else:
                try:
                    with tarfile.open(tmp_file, "r:*") as tf:
                        _safe_extract_tar(tf, extract_dir)
                except Exception:
                    with zipfile.ZipFile(tmp_file, "r") as zf:
                        _safe_extract_zip(zf, extract_dir)
        except Exception as e:
            return JSONResponse({"status": "error", "message": f"Failed to extract archive: {e}"}, status_code=400)

        model_dir = _find_dir_with_file(extract_dir, "config.json") or extract_dir
        if not (model_dir / "config.json").exists():
            return JSONResponse({"status": "error", "message": "No HF model config.json found in archive."}, status_code=400)

        model_name = Path(file.filename or f"bert_{uuid4().hex}").stem
        # Try read config to refine name
        try:
            with open(model_dir / "config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
                arch = None
                if isinstance(cfg.get("architectures"), list) and cfg["architectures"]:
                    arch = cfg["architectures"][0]
                if cfg.get("_name_or_path"):
                    base = Path(cfg["_name_or_path"]).name
                else:
                    base = arch or "bert_model"
                model_name = f"{base}".replace("/", "_")
        except Exception:
            pass

        model_name = _unique_name(BERT_MODELS_PATH, model_name)
        dest = BERT_MODELS_PATH / model_name
        shutil.move(str(model_dir), str(dest))

        # sanity-check load quickly (optional but helpful)
        try:
            _tok = AutoTokenizer.from_pretrained(str(dest))
            _mdl = AutoModelForSequenceClassification.from_pretrained(str(dest))
            bert_cache[model_name] = pipeline("text-classification", model=_mdl, tokenizer=_tok, device=device, truncation=True)
        except Exception as e:
            logger.warning("Uploaded BERT model could not be loaded immediately: %s", e)

        _save_catalog(CATALOG)
        return JSONResponse({"status": "success", "name": model_name})
    except Exception as e:
        logger.exception("BERT upload failed")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    finally:
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

@app.post("/models/bert/from_hf")
async def add_bert_from_hf(req: HFRequest, current_user=Depends(get_current_user_dep)):
    if not TORCH_AVAILABLE:
        return JSONResponse({"status": "error", "message": "PyTorch is not available in this Python environment. Install torch to add/activate BERT models from Hugging Face."}, status_code=400)

    repo = (req.repo or "").trim()
    if not repo:
        return JSONResponse({"status": "error", "message": "Missing repo."}, status_code=400)
    try:
        # Prime local HF cache by loading once (fast fail if invalid)
        tok = AutoTokenizer.from_pretrained(repo)
        mdl = AutoModelForSequenceClassification.from_pretrained(repo)
        pl = pipeline("text-classification", model=mdl, tokenizer=tok, device=device, truncation=True)
        bert_cache[repo] = pl  # cache it
        if repo not in CATALOG.get("bert_hf", []):
            CATALOG.setdefault("bert_hf", []).append(repo)
        _save_catalog(CATALOG)
        return JSONResponse({"status": "success", "name": repo})
    except Exception as e:
        logger.exception("Failed to add model from HF: %s", repo)
        return JSONResponse({"status": "error", "message": f"Could not load from HF repo '{repo}': {e}"}, status_code=400)

# =========================
# Existing processing route (unchanged behavior)
# =========================
@app.post("/process/")
async def process_file(
    file: UploadFile = File(...),
    model_choice: str = Form("bert"),
    entity_types: str = Form("all"),
    prompt: Optional[str] = Form(None),
    examples: Optional[str] = Form(None),
    model_id: Optional[str] = Form("gemini-2.5-pro"),
    current_user=Depends(get_current_user_dep),
):
    tmp_path: Optional[Path] = None
    try:
        suffix = Path(file.filename).suffix if file.filename else ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        # Extract text
        doc_text = ""
        try:
            if DOCLING_AVAILABLE and converter:
                result = converter.convert(tmp_path)
                docling_doc = result.document
                doc_text = docling_doc.export_to_markdown() or docling_doc.export_to_text() or ""
            else:
                with fitz.open(str(tmp_path)) as doc:
                    for page_num in range(doc.page_count):
                        doc_text += doc[page_num].get_text("text") + "\n"
        except Exception:
            try:
                with fitz.open(str(tmp_path)) as doc:
                    for page_num in range(doc.page_count):
                        doc_text += doc[page_num].get_text("text") + "\n"
            except Exception:
                doc_text = ""

        # ----- LangExtract branch (unchanged) -----
        if model_choice.lower() == "langextract":
            if not LANGEXTRACT_AVAILABLE:
                return JSONResponse(
                    {"status": "error", "message": "LangExtract not installed. pip install langextract"},
                    status_code=400,
                )
            api_key = os.getenv("LANGEXTRACT_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return JSONResponse(
                    {"status": "error", "message": "Missing API key for LangExtract (LANGEXTRACT_API_KEY or GOOGLE_API_KEY)."},
                    status_code=400,
                )
            example_objs = _parse_langextract_examples(examples)
            default_prompt = (
                "Extract entities and their attributes from the text. "
                "Use exact spans from the text, do not paraphrase or overlap entities."
            )
            try:
                lx_result = lx.extract(
                    text_or_documents=doc_text or "",
                    prompt_description=prompt or default_prompt,
                    examples=example_objs if example_objs else None,
                    model_id=model_id or "gemini-2.5-pro",
                    api_key=api_key,
                )
            except Exception as e:
                logging.exception("LangExtract failed: %s", e)
                return JSONResponse({"status": "error", "message": f"LangExtract extraction failed: {e}"}, status_code=500)

            html_content = ""
            tmp_jsonl_path = None
            try:
                tmp_dir = tempfile.mkdtemp(prefix="langex_")
                tmp_jsonl_path = os.path.join(tmp_dir, f"extraction_{uuid4().hex}.jsonl")
                lx.io.save_annotated_documents([lx_result], output_name=tmp_jsonl_path)
                html_content = lx.visualize(tmp_jsonl_path)
            finally:
                try:
                    if tmp_jsonl_path and os.path.exists(tmp_jsonl_path):
                        os.remove(tmp_jsonl_path)
                        shutil.rmtree(os.path.dirname(tmp_jsonl_path), ignore_errors=True)
                except Exception:
                    pass

            le_entities = _flatten_langextract_entities(lx_result)
            return JSONResponse(
                {
                    "status": "success",
                    "model": "langextract",
                    "text": doc_text,
                    "entities": le_entities,
                    "file_type": (suffix.lower().lstrip(".") if suffix else "pdf"),
                    "pdf_highlights": [],
                    "pdf_url": f"/download/{tmp_path.name}" if tmp_path else None,
                    "visualization_html": html_content,
                }
            )

        # ----- spaCy branch (unchanged behavior; manual displaCy with regex merge) -----
        if model_choice.lower() == "spacy":
            if not SPACY_AVAILABLE or SPACY_NLP is None:
                return JSONResponse(
                    {"status": "error", "message": "spaCy model not available. pip install spacy && python -m spacy download en_core_web_sm"},
                    status_code=400,
                )
            doc = SPACY_NLP(doc_text or "")
            spacy_filter, custom_filter = _compute_spacy_and_custom_filters(entity_types, SPACY_LABELS)
            selected_any = entity_types and entity_types != "all"
            manual_ents: List[Dict[str, Any]] = []
            for ent in doc.ents:
                allow_spacy = (spacy_filter is None) or (ent.label_.upper() in spacy_filter)
                if allow_spacy:
                    _add_non_overlapping_span(manual_ents, ent.start_char, ent.end_char, ent.label_.upper())
            for m in run_regex_on_text(doc_text or ""):
                lbl = m["label"].upper()
                allow_custom = (custom_filter is None) or (lbl in custom_filter)
                if allow_custom:
                    _add_non_overlapping_span(manual_ents, m["start"], m["end"], lbl)
            if selected_any and len(manual_ents) == 0:
                for ent in doc.ents:
                    _add_non_overlapping_span(manual_ents, ent.start_char, ent.end_char, ent.label_.upper())
            manual_ents.sort(key=lambda x: (x["start"], x["end"]))
            displacy_input = [{"text": doc_text or "", "ents": manual_ents, "title": None}]
            spacy_html = displacy.render(displacy_input, style="ent", manual=True, page=True, options={"colors": SPACY_COLORS})
            ents_for_table = []
            for e in manual_ents:
                span_text = (doc_text or "")[e["start"]: e["end"]]
                ents_for_table.append({"text": span_text, "label": e["label"], "start": e["start"], "end": e["end"], "page": "-"})
            return JSONResponse(
                {
                    "status": "success",
                    "model": "spacy",
                    "text": doc_text,
                    "entities": ents_for_table,
                    "file_type": (suffix.lower().lstrip(".") if suffix else "pdf"),
                    "pdf_highlights": [],
                    "pdf_url": f"/download/{tmp_path.name}" if tmp_path else None,
                    "spacy_visualization_html": spacy_html,
                    "spacy_labels_used": sorted(list(set([e["label"] for e in manual_ents]))),
                }
            )

        # ----- FinBERT sentiment branch (MODEL-DRIVEN PREDICTIVE ANALYSIS) -----
        if model_choice.lower() in ["bert", "finbert", "bert/finbert"]:
            if not FINBERT_READY:
                msg = f"FinBERT model '{FINBERT_MODEL_NAME}' is not available on the server."
                if not TORCH_AVAILABLE:
                    msg += " PyTorch is not installed for this Python; install torch (or run on Python 3.11/3.12) to enable FinBERT."
                return JSONResponse({"status": "error", "message": msg}, status_code=500)

            pdf_highlights: List[Dict[str, Any]] = []
            sentiment_rows: List[Dict[str, Any]] = []
            page_breakdown: Dict[int, Dict[str, int]] = {}
            counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            conf_sum = 0.0
            n_items = 0

            top_pos: List[Tuple[float, Dict[str, Any]]] = []
            top_neg: List[Tuple[float, Dict[str, Any]]] = []

            # Confidence gates for cleaner highlights
            MIN_CONF_POSNEG = float(os.getenv("FINBERT_MIN_CONF_POSNEG", "0.50"))
            MIN_CONF_NEU = float(os.getenv("FINBERT_MIN_CONF_NEU", "0.58"))

            try:
                doc = fitz.open(str(tmp_path))
            except Exception:
                doc = None

            if doc:
                for page_index in range(doc.page_count):
                    page = doc[page_index]
                    info = build_page_token_stream(page)
                    page_text = info["page_text"]
                    tokens = info["tokens"]
                    pw, ph = info["page_width"], info["page_height"]

                    spans = _sentence_spans(page_text)
                    if not spans:
                        continue

                    texts = [page_text[s:e].strip() for (s, e) in spans]

                    # Batch classify sentences
                    batch_results = finbert_pipeline(texts, return_all_scores=True, truncation=True)
                    # Normalize shape if HF returns list[dict] for single item
                    if texts and isinstance(batch_results, list) and (len(batch_results) > 0) and isinstance(batch_results[0], dict):
                        batch_results = [batch_results]

                    page_pos = page_neg = page_neu = 0

                    for (start, end), sent_text, scores in zip(spans, texts, batch_results):
                        if not sent_text or not scores:
                            continue

                        score_map = { _norm_sent_label(d["label"]): float(d["score"]) for d in scores }
                        for k in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                            score_map.setdefault(k, 0.0)

                        pred_label = max(score_map, key=score_map.get)
                        conf = score_map[pred_label]

                        # Map to tokens
                        i0 = i1 = None
                        for i, t in enumerate(tokens):
                            if t["end"] <= start:
                                continue
                            if t["start"] >= end:
                                break
                            if i0 is None:
                                i0 = i
                            i1 = i
                        if i0 is not None and i1 is not None:
                            # GROUP BY LINE for tidy highlight segments
                            line_groups: Dict[float, List[int]] = {}
                            for j in range(i0, i1 + 1):
                                y0 = tokens[j]["bbox"][1]
                                line_key = round(y0, 1)  # stable line bucket
                                line_groups.setdefault(line_key, []).append(j)

                            # Apply confidence gating for highlights only
                            allow_highlight = (
                                (pred_label in ["POSITIVE", "NEGATIVE"] and conf >= MIN_CONF_POSNEG) or
                                (pred_label == "NEUTRAL" and conf >= MIN_CONF_NEU)
                            )

                            for _, idxs in sorted(line_groups.items(), key=lambda kv: kv[0]):
                                x0 = min(tokens[j]["bbox"][0] for j in idxs)
                                y0 = min(tokens[j]["bbox"][1] for j in idxs)
                                x1 = max(tokens[j]["bbox"][2] for j in idxs)
                                y1 = max(tokens[j]["bbox"][3] for j in idxs)

                                top = (y0 / ph) * 100
                                left = (x0 / pw) * 100
                                width = ((x1 - x0) / pw) * 100
                                height = ((y1 - y0) / ph) * 100

                                if allow_highlight:
                                    # sample word from token group
                                    sample_text = " ".join(tokens[j]["text"] for j in idxs)[:200]
                                    pdf_highlights.append({
                                        "page": page_index + 1,
                                        "label": pred_label,  # POSITIVE/NEGATIVE/NEUTRAL
                                        "word": sample_text,
                                        "score": round(conf, 4),
                                        "top": top, "left": left, "width": width, "height": height,
                                        "page_width": pw, "page_height": ph,
                                    })

                        # Entities table row (always keep)
                        sentiment_rows.append({
                            "page": page_index + 1,
                            "label": pred_label,
                            "text": sent_text,
                            "score": round(conf, 4),        # include score for frontend table
                            "confidence": round(conf, 4),  # backward compatibility
                            "start": start,
                            "end": end,
                        })

                        counts[pred_label] += 1
                        conf_sum += conf
                        n_items += 1

                        if pred_label == "POSITIVE":
                            page_pos += 1
                            top_pos.append((conf, {"page": page_index + 1, "text": sent_text, "score": round(conf, 4)}))
                        elif pred_label == "NEGATIVE":
                            page_neg += 1
                            top_neg.append((conf, {"page": page_index + 1, "text": sent_text, "score": round(conf, 4)}))
                        else:
                            page_neu += 1

                    page_breakdown[page_index + 1] = {"POSITIVE": page_pos, "NEGATIVE": page_neg, "NEUTRAL": page_neu}

                doc.close()

            avg_conf = round(conf_sum / n_items, 4) if n_items else 0.0
            overall_label = max(counts, key=counts.get) if n_items else "NEUTRAL"

            # Top sentences
            top_pos = sorted(top_pos, key=lambda x: x[0], reverse=True)[:3]
            top_neg = sorted(top_neg, key=lambda x: x[0], reverse=True)[:3]
            top_positive_sentences = [x[1] for x in top_pos]
            top_negative_sentences = [x[1] for x in top_neg]

            # Model-driven outlook + recommendation from distribution only
            total = max(1, n_items)
            pos_ratio = counts["POSITIVE"] / total
            neg_ratio = counts["NEGATIVE"] / total

            if pos_ratio >= 0.6 and neg_ratio <= 0.25:
                outlook = "Bullish tone with consistently positive language across sentences."
                recommendation = "Proceed to next milestone. Validate key commercial terms (pricing, SLAs, renewals) before sign-off."
            elif neg_ratio >= 0.5:
                outlook = "Bearish tone with prevalent negative language indicating higher risk."
                recommendation = "Escalate for deeper review. Prioritize negotiating the most negative sections highlighted and seek clarifications."
            else:
                outlook = "Mixed/neutral tone with a balance of positive and negative signals."
                recommendation = "Hold targeted review on the most confident negative segments; confirm alignment on obligations and timelines."

            predictive_analysis = (
                f"Overall sentiment: {overall_label} (avg confidence {avg_conf:.2f}). "
                f"Segments — Positive: {counts['POSITIVE']}, Neutral: {counts['NEUTRAL']}, Negative: {counts['NEGATIVE']}. "
                f"{outlook}\n"
            )

            if top_negative_sentences:
                neg_lines = "; ".join([f'“{s["text"][:140]}” (p{s["page"]}, {s["score"]:.2f})' for s in top_negative_sentences])
                predictive_analysis += f"Top negative examples: {neg_lines}.\n"
            if top_positive_sentences:
                pos_lines = "; ".join([f'“{s["text"][:140]}” (p{s["page"]}, {s["score"]:.2f})' for s in top_positive_sentences])
                predictive_analysis += f"Top positive examples: {pos_lines}.\n"

            predictive_analysis += f"Recommendation: {recommendation}"

            # Build top-level fields expected by frontend
            sentiment_counts = {
                "positive": counts["POSITIVE"],
                "negative": counts["NEGATIVE"],
                "neutral": counts["NEUTRAL"],
            }

            # sort/ dedup highlights a bit
            seen = set()
            dedup_highlights = []
            for h in pdf_highlights:
                key = (
                    h["page"],
                    round(h["top"], 3),
                    round(h["left"], 3),
                    round(h["width"], 3),
                    round(h["height"], 3),
                    h["label"],
                )
                if key not in seen:
                    seen.add(key)
                    dedup_highlights.append(h)

            return JSONResponse(
                {
                    "status": "success",
                    "model": "bert",
                    "text": doc_text,
                    "entities": sentiment_rows,  # sentence rows with score
                    "file_type": (suffix.lower().lstrip(".") if suffix else "pdf"),
                    "pdf_highlights": dedup_highlights,      # used by your viewer
                    "sentiment_highlights": dedup_highlights, # alias
                    "pdf_url": f"/download/{tmp_path.name}" if tmp_path else None,

                    # New model-driven predictive fields:
                    "predictive_analysis": predictive_analysis,
                    "sentiment_counts": sentiment_counts,
                    "overall_sentiment": overall_label,
                    "sentiment_summary": {
                        "overall_label": overall_label,
                        "average_confidence": avg_conf,
                        "counts": counts,
                        "total_segments": n_items,
                        "page_breakdown": page_breakdown,
                        "top_positive_sentences": top_positive_sentences,
                        "top_negative_sentences": top_negative_sentences,
                        "outlook": outlook,
                        "recommendation": recommendation,
                    },
                }
            )

        # Unknown model_choice
        return JSONResponse({"status": "error", "message": f"Unknown model_choice: {model_choice}"}, status_code=400)

    except Exception as e:
        logging.exception("Error processing file")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    finally:
        if tmp_path and tmp_path.exists():
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

@app.get("/download/{filename}")
async def download_file(filename: str):
    temp_dir_path = Path(tempfile.gettempdir())
    file_path = temp_dir_path / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    return JSONResponse({"status": "error", "message": "File not found or already cleaned up"}, status_code=404)