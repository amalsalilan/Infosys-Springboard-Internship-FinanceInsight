from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional
import os
import sys
import io
import json
import unicodedata
import warnings
from pathlib import Path

# Suppress warnings from external libraries
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2")

# Force UTF-8 encoding for stdout/stderr on Windows to handle special Unicode characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set environment variable for UTF-8 mode (Python 3.7+)
if hasattr(sys, 'set_int_max_str_digits'):
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/langextract_service.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Import langextract after configuring warnings
import langextract as lx

app = FastAPI(
    title="LangExtract Service",
    description="API for extracting structured information from text using LLMs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API key configuration
# IMPORTANT: Get your own API key from https://ai.google.dev/gemini-api/docs/api-key
# The hardcoded key below may be invalid or expired
API_KEY = os.getenv("LANGEXTRACT_API_KEY", "AIzaSyCJH2lOrks1C_faZxubvEYAIb2rw7yHIV8")
if API_KEY and API_KEY != "":
    os.environ["LANGEXTRACT_API_KEY"] = API_KEY

# Pre-load LangExtract to avoid loading plugins on every request
logger.info("Pre-loading LangExtract provider plugins...")
try:
    # Initialize LangExtract by importing and testing availability
    _ = lx.data.Extraction
    logger.info("LangExtract pre-loaded successfully")
except Exception as e:
    logger.warning(f"Could not pre-load LangExtract: {e}")


def normalize_unicode_text(text: str) -> str:
    """
    Normalize Unicode text to handle special characters consistently.
    Uses NFC (Canonical Decomposition, followed by Canonical Composition).

    Args:
        text: Input text that may contain special Unicode characters

    Returns:
        Normalized text safe for processing
    """
    if not text:
        return text
    # Normalize to NFC form (most compatible)
    return unicodedata.normalize('NFC', text)


class ExtractionAttribute(BaseModel):
    """Attributes for an extraction"""
    pass


class ExampleExtraction(BaseModel):
    """Single extraction in an example"""
    extraction_class: str
    extraction_text: str
    attributes: Dict[str, str]


class Example(BaseModel):
    """Example data to guide the model"""
    text: str
    extractions: List[ExampleExtraction]


class ExtractRequest(BaseModel):
    """Request model for extraction"""
    text: str
    prompt_description: str
    examples: List[Example]
    model_id: str = "gemini-2.0-flash-exp"  # Using experimental flash model


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LangExtract Service",
        "model": "Gemini (via LangExtract)",
        "endpoints": {
            "POST /extract": "Extract structured information from text",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "langextract"
    }


@app.post("/extract")
async def extract_information(request: ExtractRequest):
    """
    Extract structured information from text using LangExtract

    Args:
        request: ExtractRequest with text, prompt, examples, and model_id

    Returns:
        JSON response with extractions and HTML visualization
    """
    logger.info(f"Received extraction request for text of length {len(request.text)} with {len(request.examples)} examples")

    try:
        # Check if API key is configured
        if not API_KEY or API_KEY == "":
            logger.error("LangExtract API key not configured")
            raise HTTPException(
                status_code=503,
                detail="LangExtract API key not configured. Please set LANGEXTRACT_API_KEY environment variable."
            )

        # Normalize input text to handle Unicode characters properly
        logger.debug("Normalizing input text and prompt...")
        normalized_text = normalize_unicode_text(request.text)
        normalized_prompt = normalize_unicode_text(request.prompt_description)

        # Convert request examples to LangExtract format
        logger.debug(f"Converting {len(request.examples)} examples to LangExtract format...")
        lx_examples = []
        for example in request.examples:
            lx_extractions = [
                lx.data.Extraction(
                    extraction_class=normalize_unicode_text(ext.extraction_class),
                    extraction_text=normalize_unicode_text(ext.extraction_text),
                    attributes={k: normalize_unicode_text(v) for k, v in ext.attributes.items()}
                )
                for ext in example.extractions
            ]

            lx_examples.append(
                lx.data.ExampleData(
                    text=normalize_unicode_text(example.text),
                    extractions=lx_extractions
                )
            )
        logger.debug("Examples converted successfully")

        # Run the extraction with normalized text and timeout handling
        import asyncio
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

        def run_extraction():
            start_time = time.time()
            logger.info(f"Running extraction with model {request.model_id}...")
            result = lx.extract(
                text_or_documents=normalized_text,
                prompt_description=normalized_prompt,
                examples=lx_examples,
                model_id=request.model_id,
            )
            elapsed_time = time.time() - start_time
            logger.info(f"Extraction completed in {elapsed_time:.2f} seconds")
            return result

        # Run extraction in thread pool with 30 second timeout
        logger.info("Starting extraction in thread pool with 30s timeout...")
        extraction_start = time.time()
        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_extraction)
            try:
                result = future.result(timeout=30)
                total_time = time.time() - extraction_start
                logger.info(f"Total extraction time (including overhead): {total_time:.2f}s")
            except FuturesTimeoutError:
                logger.error("Extraction timed out after 30 seconds")
                raise HTTPException(
                    status_code=504,
                    detail="Extraction timed out after 30 seconds. The Gemini API may be unavailable or the text is too long."
                )
            except Exception as e:
                # Catch specific API errors
                error_msg = str(e)
                logger.error(f"Extraction failed: {error_msg}")
                if "invalid argument" in error_msg.lower() or "errno 22" in error_msg.lower():
                    raise HTTPException(
                        status_code=500,
                        detail="API configuration error. The Gemini API key may be invalid or expired. Please check your API key."
                    )
                raise

        # Save results to JSONL file with explicit UTF-8 encoding
        logger.info("Saving extraction results...")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "extraction_results.jsonl")

        # Calculate positions using LangExtract's CharInterval format
        text_for_search = result.text if hasattr(result, 'text') else ""
        extractions_with_positions = []

        for ext in (result.extractions if hasattr(result, 'extractions') else []):
            ext_dict = {
                "extraction_class": ext.extraction_class,
                "extraction_text": ext.extraction_text,
                "attributes": ext.attributes
            }

            # Try to find position in text and add char_interval
            if text_for_search and ext.extraction_text:
                start_pos = text_for_search.find(ext.extraction_text)
                if start_pos != -1:
                    # Use LangExtract's char_interval format with start_pos and end_pos
                    ext_dict["char_interval"] = {
                        "start_pos": start_pos,
                        "end_pos": start_pos + len(ext.extraction_text)
                    }

            extractions_with_positions.append(ext_dict)

        result_dict = {
            "text": text_for_search,
            "extractions": extractions_with_positions
        }

        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(result_dict, f, ensure_ascii=False)
            f.write('\n')
        logger.info(f"Saved extraction results to {output_file} with {len(extractions_with_positions)} extractions")

        # Generate HTML visualization
        logger.info("Generating HTML visualization...")
        html_content = lx.visualize(output_file)

        # Handle both Jupyter and regular output
        if hasattr(html_content, 'data'):
            html_output = html_content.data
        else:
            html_output = html_content

        # Add data-extraction-index attributes to HTML for navigation
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_output, 'html.parser')

        # Find all highlighted spans (LangExtract uses marks or specific classes)
        # The exact selector depends on how lx.visualize() structures the HTML
        highlighted_elements = soup.find_all('mark') or soup.find_all(class_=lambda x: x and 'highlight' in x.lower() if x else False)

        # If we can't find marks, look for spans with background colors or specific attributes
        if not highlighted_elements:
            highlighted_elements = soup.find_all('span', style=lambda x: x and 'background' in x.lower() if x else False)

        # Add index to each highlighted element
        for index, element in enumerate(highlighted_elements):
            element['data-extraction-index'] = str(index)

        html_output = str(soup)

        # Save HTML visualization
        html_file = os.path.join(output_dir, "extraction_visualization.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_output)
        logger.info(f"Saved HTML visualization to {html_file}")

        # Convert result to dictionary for JSON response
        extractions = []
        if hasattr(result, 'extractions'):
            for ext in result.extractions:
                ext_dict = {
                    "extraction_class": ext.extraction_class,
                    "extraction_text": ext.extraction_text,
                    "attributes": ext.attributes
                }
                if hasattr(ext, 'start_char'):
                    ext_dict["start_char"] = ext.start_char
                if hasattr(ext, 'end_char'):
                    ext_dict["end_char"] = ext.end_char
                extractions.append(ext_dict)

        logger.info(f"Extraction completed successfully with {len(extractions)} extractions")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "extractions": extractions,
                "html_visualization": html_output,
                "saved_files": {
                    "jsonl": output_file,
                    "html": html_file
                }
            }
        )

    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during extraction: {str(e)}"
        )


@app.get("/visualization")
async def get_visualization():
    """
    Get the latest HTML visualization

    Returns:
        HTML visualization of the last extraction
    """
    html_file = os.path.join("output", "extraction_visualization.html")

    if not os.path.exists(html_file):
        raise HTTPException(
            status_code=404,
            detail="No visualization found. Run an extraction first."
        )

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)

