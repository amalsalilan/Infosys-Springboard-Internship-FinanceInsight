from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path
from docling.document_converter import DocumentConverter
import httpx
from typing import Optional

app = FastAPI(
    title="Document to Markdown Converter",
    description="API for converting documents (DOCX, XLSX, PPTX, PDF, HTML, CSV, Markdown, AsciiDoc) to Markdown format",
    version="1.0.0"
)

# Development setting: Save outputs to folder (1=save, 0=don't save)
OUTPUT_SAVING = 1

# Initialize Docling converter
converter = DocumentConverter()

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
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Create temporary file to store upload
    temp_file = None
    try:
        # Read file content
        content = await file.read()

        # Create temporary file with proper extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Convert document to markdown using Docling
        result = converter.convert(temp_file_path)
        markdown_content = result.document.export_to_markdown()
        text_content = result.document.export_to_text()
        html_content = result.document.export_to_html()

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

            # Save HTML
            html_path = output_dir / f"{base_name}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            saved_files["html"] = str(html_path)

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

        return JSONResponse(status_code=200, content=response_data)

    except Exception as e:
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
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in SUPPORTED_FORMATS:
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

        # Use markdown for better structure preservation, fallback to text if markdown is poor
        analysis_text = markdown_content if markdown_content and len(markdown_content) > len(text_content) * 0.5 else text_content

        # Call sentiment analysis API
        async with httpx.AsyncClient(timeout=30.0) as client:
            sentiment_response = await client.post(
                sentiment_api_url,
                json={"text": analysis_text, "analyze_by_paragraph": True}
            )

            if sentiment_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Sentiment analysis failed: {sentiment_response.text}"
                )

            sentiment_data = sentiment_response.json()

        # Import HTML annotator
        from html_annotator import create_simple_annotated_html

        # Create annotated HTML
        sentiment_results = [
            {
                "text": p["text"],
                "sentiment": p["sentiment"],
                "confidence": p["confidence"]
            }
            for p in sentiment_data.get("paragraphs", [])
        ]

        # Use the same text for annotation that was used for analysis
        annotated_html = create_simple_annotated_html(sentiment_results, analysis_text)

        # Save HTML to file automatically
        output_filename = f"{Path(file.filename).stem}_sentiment_analysis.html"
        output_path = os.path.join(os.getcwd(), "output", output_filename)

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(annotated_html)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": file.filename,
                "format": file_extension,
                "markdown": markdown_content,
                "text": text_content,
                "sentiment_analysis": {
                    "overall_sentiment": sentiment_data.get("overall_sentiment"),
                    "overall_confidence": sentiment_data.get("overall_confidence"),
                    "paragraphs": sentiment_results
                },
                "annotated_html": annotated_html,
                "html_saved_to": output_path
            }
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with sentiment API: {str(e)}"
        )
    except Exception as e:
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
