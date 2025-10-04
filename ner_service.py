from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import os

app = FastAPI(
    title="Financial NER Service",
    description="API for Named Entity Recognition in financial documents",
    version="1.0.0"
)

# Global NER pipeline
ner_pipeline = None

# Financial NER model - using a popular financial NER model
MODEL_NAME = "dslim/bert-base-NER"  # General NER model (works for financial text)


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


@app.on_event("startup")
async def load_model():
    """Load NER model on startup"""
    global ner_pipeline
    print(f"Loading NER model: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    print("NER model loaded successfully!")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Financial NER Service",
        "model": MODEL_NAME,
        "endpoints": {
            "POST /recognize": "Recognize financial entities in text",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = ner_pipeline is not None
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "service": "financial-ner",
        "model_loaded": model_loaded
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

    # Extract base entity type (remove B- or I- prefix if exists)
    base_entity = entity_type.replace("B-", "").replace("I-", "")

    return colors.get(base_entity, "#E0E0E0")  # Default gray


def highlight_entities_in_html(text: str, entities: List[Dict]) -> str:
    """
    Highlight entities in HTML

    Args:
        text: Original text
        entities: List of entities with positions

    Returns:
        HTML string with highlighted entities
    """
    # Sort entities by start position in reverse order
    sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)

    highlighted_text = text

    for entity in sorted_entities:
        start = entity['start']
        end = entity['end']
        entity_text = entity['word']
        entity_type = entity['entity_group']
        score = entity['score']
        color = get_entity_color(entity_type)

        # Create highlighted span with tooltip
        highlighted = f'<span style="background-color: {color}; padding: 2px 4px; border-radius: 3px; margin: 0 2px;" title="{entity_type} (confidence: {score:.2f})">{entity_text}</span>'

        # Replace in text
        highlighted_text = highlighted_text[:start] + highlighted + highlighted_text[end:]

    # Wrap in HTML structure
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
            line-height: 1.6;
        }}
        .legend {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 15px;
            margin-bottom: 5px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            vertical-align: middle;
            border-radius: 3px;
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
    <h1>Financial Entity Recognition Results</h1>
    <div class="legend">
        <strong>Entity Types:</strong><br>
        <div class="legend-item"><span class="legend-color" style="background-color: #FFB6C1;"></span>Person</div>
        <div class="legend-item"><span class="legend-color" style="background-color: #ADD8E6;"></span>Organization</div>
        <div class="legend-item"><span class="legend-color" style="background-color: #90EE90;"></span>Location</div>
        <div class="legend-item"><span class="legend-color" style="background-color: #98FB98;"></span>Money</div>
        <div class="legend-item"><span class="legend-color" style="background-color: #F0E68C;"></span>Date</div>
        <div class="legend-item"><span class="legend-color" style="background-color: #FFDAB9;"></span>Percent</div>
        <div class="legend-item"><span class="legend-color" style="background-color: #FFE4B5;"></span>Miscellaneous</div>
    </div>
    <div class="content">
        {highlighted_text}
    </div>
</body>
</html>"""

    return html_output


@app.post("/recognize")
async def recognize_entities(request: NERRequest):
    """
    Recognize named entities in text

    Args:
        request: NERRequest with text

    Returns:
        JSON response with entities and highlighted HTML
    """
    if not ner_pipeline:
        raise HTTPException(
            status_code=503,
            detail="NER model not loaded. Please wait for service to initialize."
        )

    try:
        # Run NER
        entities = ner_pipeline(request.text)

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

        # Generate highlighted HTML
        highlighted_html = highlight_entities_in_html(request.text, entities)

        # Save HTML to output folder
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        html_file = os.path.join(output_dir, "ner_results.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(highlighted_html)

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
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error during NER: {str(e)}"
        )


@app.get("/visualization")
async def get_visualization():
    """
    Get the latest HTML visualization

    Returns:
        HTML visualization of the last NER result
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
