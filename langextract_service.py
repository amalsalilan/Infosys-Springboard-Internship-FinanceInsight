from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import langextract as lx
import os

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

# Hardcoded Gemini API key (for testing only)
API_KEY = "AIzaSyCJH2lOrks1C_faZxubvEYAIb2rw7yHIV8"
os.environ["LANGEXTRACT_API_KEY"] = API_KEY


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
    model_id: str = "gemini-2.0-flash-exp"


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
    try:
        # Convert request examples to LangExtract format
        lx_examples = []
        for example in request.examples:
            lx_extractions = [
                lx.data.Extraction(
                    extraction_class=ext.extraction_class,
                    extraction_text=ext.extraction_text,
                    attributes=ext.attributes
                )
                for ext in example.extractions
            ]

            lx_examples.append(
                lx.data.ExampleData(
                    text=example.text,
                    extractions=lx_extractions
                )
            )

        # Run the extraction
        result = lx.extract(
            text_or_documents=request.text,
            prompt_description=request.prompt_description,
            examples=lx_examples,
            model_id=request.model_id,
        )

        # Save results to JSONL file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "extraction_results.jsonl")
        lx.io.save_annotated_documents([result], output_name="extraction_results.jsonl", output_dir=output_dir)

        # Generate HTML visualization
        html_content = lx.visualize(output_file)

        # Handle both Jupyter and regular output
        if hasattr(html_content, 'data'):
            html_output = html_content.data
        else:
            html_output = html_content

        # Save HTML visualization
        html_file = os.path.join(output_dir, "extraction_visualization.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_output)

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
        import traceback
        traceback.print_exc()
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
