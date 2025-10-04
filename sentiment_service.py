from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
from bs4 import BeautifulSoup

app = FastAPI(
    title="Sentiment Analysis Service",
    description="API for analyzing sentiment in financial documents using FinBERT",
    version="1.0.0"
)

# Global model and tokenizer (loaded once at startup)
model = None
tokenizer = None


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


@app.on_event("startup")
async def load_model():
    """Load FinBERT model on startup"""
    global model, tokenizer
    print("Loading FinBERT model...")
    model_name = "ProsusAI/finbert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    print("FinBERT model loaded successfully!")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Sentiment Analysis Service",
        "model": "FinBERT (ProsusAI/finbert)",
        "endpoints": {
            "POST /analyze": "Analyze sentiment of text and optionally highlight HTML",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = model is not None and tokenizer is not None
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "service": "sentiment-analysis",
        "model_loaded": model_loaded
    }


def split_into_sentences(text: str) -> List[Dict]:
    """Split text into sentences and return with character positions."""
    sentences_with_positions = []
    current_pos = 0

    # Split sentences using regex
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)

    for sentence in sentences:
        if sentence.strip():
            # Find the actual position in original text
            start_pos = text.find(sentence, current_pos)
            end_pos = start_pos + len(sentence)

            sentences_with_positions.append({
                'text': sentence,
                'start': start_pos,
                'end': end_pos
            })

            current_pos = end_pos

    return sentences_with_positions


def analyze_sentiment(text: str) -> tuple:
    """Analyze sentiment using FinBERT model."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_score = predictions[0].tolist()

    # FinBERT labels: positive, negative, neutral
    labels = ['positive', 'negative', 'neutral']
    sentiment_class = labels[sentiment_score.index(max(sentiment_score))]

    return sentiment_class, {
        'positive': sentiment_score[0],
        'negative': sentiment_score[1],
        'neutral': sentiment_score[2]
    }


def get_highlight_color(sentiment_class: str, scores: Dict[str, float]) -> Optional[str]:
    """Get color based on sentiment and confidence score."""
    if sentiment_class == 'neutral':
        return None  # Skip neutral sentences

    if sentiment_class == 'positive':
        # Green intensity based on confidence score (0.0 to 1.0)
        # Higher confidence = darker green (lower R and B values)
        base_lightness = 255 - int(scores['positive'] * 155)  # Range: 255 to 100
        return f'rgb({base_lightness}, 255, {base_lightness})'

    elif sentiment_class == 'negative':
        # Red intensity based on confidence score
        # Higher confidence = darker red (lower G and B values)
        base_lightness = 255 - int(scores['negative'] * 155)  # Range: 255 to 100
        return f'rgb(255, {base_lightness}, {base_lightness})'

    return None


def highlight_html(html_content: str, sentiment_results: List[Dict]) -> str:
    """Apply sentiment highlighting to HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    html_str = str(soup)

    # Sort sentiments by position (start) in reverse to avoid position shifts
    sentiments_sorted = sorted(sentiment_results, key=lambda x: x['position']['start'], reverse=True)

    # Apply highlights
    for sentiment in sentiments_sorted:
        color = get_highlight_color(sentiment['class'], sentiment['confidence_scores'])

        if color:  # Skip neutral
            sentence = sentiment['sentence']
            # Create highlighted version
            highlighted = f'<span style="background-color: {color};">{sentence}</span>'

            # Replace in HTML
            html_str = html_str.replace(sentence, highlighted, 1)

    return html_str


@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment_endpoint(request: SentimentRequest):
    """
    Analyze sentiment of provided text and optionally highlight HTML.

    Args:
        request: SentimentRequest with text and optional html

    Returns:
        SentimentResponse with sentiment results and highlighted HTML
    """
    if not model or not tokenizer:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please wait for service to initialize."
        )

    try:
        # Split text into sentences
        sentences = split_into_sentences(request.text)

        if not sentences:
            raise HTTPException(
                status_code=400,
                detail="No sentences found in the provided text."
            )

        # Analyze sentiment for each sentence
        results = []
        for sentence_data in sentences:
            sentiment_class, scores = analyze_sentiment(sentence_data['text'])

            results.append({
                "sentence": sentence_data['text'],
                "class": sentiment_class,
                "position": {
                    "start": sentence_data['start'],
                    "end": sentence_data['end']
                },
                "confidence_scores": scores
            })

        # Generate highlighted HTML if provided
        highlighted_html = None
        if request.html:
            highlighted_html = highlight_html(request.html, results)

        return SentimentResponse(
            sentiment_results=results,
            highlighted_html=highlighted_html
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing sentiment: {str(e)}"
        )
