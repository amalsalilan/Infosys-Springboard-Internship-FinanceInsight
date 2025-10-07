from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import tempfile
import os
import json
import logging
import sys
import warnings
from pathlib import Path
from docling.document_converter import DocumentConverter
import httpx
from typing import Optional

# Suppress warnings from external libraries
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/document_converter.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document to Markdown Converter",
    description="API for converting documents (DOCX, XLSX, PPTX, PDF, HTML, CSV, Markdown, AsciiDoc) to Markdown format",
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

# Development setting: Save outputs to folder (1=save, 0=don't save)
OUTPUT_SAVING = 1

# Initialize Docling converter
logger.info("Initializing Docling DocumentConverter...")
converter = DocumentConverter()
logger.info("DocumentConverter initialized successfully")

# Supported file extensions
SUPPORTED_FORMATS = {
    '.docx', '.xlsx', '.pptx',  # MS Office formats
    '.pdf',                      # PDF
    '.html', '.xhtml',          # HTML formats
    '.csv',                      # CSV
    '.md', '.markdown',         # Markdown
    '.adoc', '.asciidoc'        # AsciiDoc
}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document to Markdown Converter API",
        "supported_formats": list(SUPPORTED_FORMATS),
        "endpoints": {
            "POST /convert": "Convert document to markdown/text",
            "POST /convert-with-sentiment": "Convert document and analyze sentiment with HTML annotation",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "document-converter"}


@app.post("/convert")
async def convert_to_markdown(file: UploadFile = File(...)):
    """
    Convert uploaded document to markdown format

    Args:
        file: Uploaded file in supported format

    Returns:
        JSON response with markdown content
    """
    logger.info(f"Received conversion request for file: {file.filename}")

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported file format attempted: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Create temporary file to store upload
    temp_file = None
    try:
        # Read file content
        content = await file.read()
        logger.info(f"Read {len(content)} bytes from uploaded file")

        # Create temporary file with proper extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        logger.debug(f"Created temporary file: {temp_file_path}")

        # Convert document to markdown using Docling
        logger.info(f"Converting document {file.filename} to markdown...")
        result = converter.convert(temp_file_path)
        markdown_content = result.document.export_to_markdown()
        text_content = result.document.export_to_text()
        html_content_raw = result.document.export_to_html()
        logger.info(f"Conversion completed successfully. Generated {len(text_content)} chars of text")

        # Inject custom CSS to make content fill full width (remove card-style layout)
        custom_css = """
        <style>
            /* Override Docling's default card/centered layout */
            html, body {
                max-width: 100% !important;
                width: 100% !important;
                height: 100% !important;
                min-height: 100% !important;
                margin: 0 !important;
                padding: 30px !important;
                box-sizing: border-box !important;
                background-color: #ffffff !important;
                background: #ffffff !important;
            }
            .document, main, article, .container, .content {
                max-width: 100% !important;
                width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                box-shadow: none !important;
                border: none !important;
                background-color: #ffffff !important;
            }
            /* Ensure headings and paragraphs use full width */
            h1, h2, h3, h4, h5, h6, p, div, section {
                max-width: 100% !important;
            }
        </style>
        """

        # Insert custom CSS before </head> or at the beginning if no </head>
        if "</head>" in html_content_raw:
            html_content = html_content_raw.replace("</head>", f"{custom_css}</head>")
        elif "<head>" in html_content_raw:
            html_content = html_content_raw.replace("<head>", f"<head>{custom_css}")
        else:
            # No head tag, wrap content
            html_content = f"<!DOCTYPE html><html><head>{custom_css}</head><body>{html_content_raw}</body></html>"

        # Save outputs if enabled
        saved_files = {}
        if OUTPUT_SAVING == 1:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            base_name = Path(file.filename).stem

            # Save text
            text_path = output_dir / f"{base_name}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            saved_files["text"] = str(text_path)
            logger.debug(f"Saved text output to {text_path}")

            # Save markdown
            md_path = output_dir / f"{base_name}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            saved_files["markdown"] = str(md_path)
            logger.debug(f"Saved markdown output to {md_path}")

            # Save HTML
            html_path = output_dir / f"{base_name}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            saved_files["html"] = str(html_path)
            logger.debug(f"Saved HTML output to {html_path}")

        response_data = {
            "success": True,
            "filename": file.filename,
            "format": file_extension,
            "markdown": markdown_content,
            "text": text_content,
            "html": html_content
        }

        if OUTPUT_SAVING == 1:
            response_data["saved_files"] = saved_files

        logger.info(f"Successfully converted {file.filename}")
        return JSONResponse(status_code=200, content=response_data)

    except Exception as e:
        logger.error(f"Error converting document {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error converting document: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass


@app.post("/convert-with-sentiment")
async def convert_with_sentiment_analysis(
    file: UploadFile = File(...),
    sentiment_api_url: str = "http://localhost:8001/analyze"
):
    """
    Convert document and analyze sentiment with HTML annotation

    Args:
        file: Uploaded file in supported format
        sentiment_api_url: URL of sentiment analysis API (default: http://localhost:8001/analyze)

    Returns:
        JSON response with markdown, text, sentiment analysis, and annotated HTML
    """
    logger.info(f"Received conversion with sentiment analysis request for file: {file.filename}")

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported file format attempted: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )

    temp_file = None
    try:
        # Read file content
        content = await file.read()

        # Create temporary file with proper extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Convert document using Docling
        result = converter.convert(temp_file_path)
        markdown_content = result.document.export_to_markdown()
        text_content = result.document.export_to_text()
        html_content_raw = result.document.export_to_html()

        # Inject custom CSS to make content fill full width (same as /convert endpoint)
        custom_css = """
        <style>
            /* Override Docling's default card/centered layout */
            html, body {
                max-width: 100% !important;
                width: 100% !important;
                height: 100% !important;
                min-height: 100% !important;
                margin: 0 !important;
                padding: 30px !important;
                box-sizing: border-box !important;
                background-color: #ffffff !important;
                background: #ffffff !important;
            }
            .document, main, article, .container, .content {
                max-width: 100% !important;
                width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                box-shadow: none !important;
                border: none !important;
                background-color: #ffffff !important;
            }
            /* Ensure headings and paragraphs use full width */
            h1, h2, h3, h4, h5, h6, p, div, section {
                max-width: 100% !important;
            }
        </style>
        """

        # Insert custom CSS before </head> or at the beginning if no </head>
        if "</head>" in html_content_raw:
            html_content = html_content_raw.replace("</head>", f"{custom_css}</head>")
        elif "<head>" in html_content_raw:
            html_content = html_content_raw.replace("<head>", f"<head>{custom_css}")
        else:
            html_content = f"<!DOCTYPE html><html><head>{custom_css}</head><body>{html_content_raw}</body></html>"

        # Use markdown for better structure preservation, fallback to text if markdown is poor
        analysis_text = markdown_content if markdown_content and len(markdown_content) > len(text_content) * 0.5 else text_content

        # Call sentiment analysis API with both text and HTML
        logger.info(f"Calling sentiment analysis API at {sentiment_api_url}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            sentiment_response = await client.post(
                sentiment_api_url,
                json={"text": analysis_text, "html": html_content}
            )

            if sentiment_response.status_code != 200:
                logger.error(f"Sentiment analysis failed with status {sentiment_response.status_code}: {sentiment_response.text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Sentiment analysis failed: {sentiment_response.text}"
                )

            sentiment_data = sentiment_response.json()
        logger.info("Sentiment analysis completed successfully")

        # Get sentiment results and highlighted HTML
        sentiment_results = sentiment_data.get("sentiment_results", [])
        annotated_html = sentiment_data.get("highlighted_html", "")

        # Save outputs if enabled
        saved_files = {}
        if OUTPUT_SAVING == 1:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            base_name = Path(file.filename).stem

            # Save text
            text_path = output_dir / f"{base_name}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            saved_files["text"] = str(text_path)

            # Save markdown
            md_path = output_dir / f"{base_name}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            saved_files["markdown"] = str(md_path)

            # Save sentiment results as JSON
            sentiment_json_path = output_dir / f"{base_name}_sentiment.json"
            with open(sentiment_json_path, 'w', encoding='utf-8') as f:
                json.dump(sentiment_results, f, indent=2, ensure_ascii=False)
            saved_files["sentiment_json"] = str(sentiment_json_path)

            # Save annotated HTML if available
            if annotated_html:
                html_path = output_dir / f"{base_name}_sentiment.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(annotated_html)
                saved_files["annotated_html"] = str(html_path)

        response_data = {
            "success": True,
            "filename": file.filename,
            "format": file_extension,
            "markdown": markdown_content,
            "text": text_content,
            "sentiment_results": sentiment_results,
            "annotated_html": annotated_html
        }

        if OUTPUT_SAVING == 1:
            response_data["saved_files"] = saved_files

        logger.info(f"Successfully converted {file.filename} with sentiment analysis")
        return JSONResponse(status_code=200, content=response_data)

    except httpx.HTTPError as e:
        logger.error(f"HTTP Error communicating with sentiment API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with sentiment API: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
