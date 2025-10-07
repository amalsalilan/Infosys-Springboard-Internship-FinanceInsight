# Document to Markdown Converter API

FastAPI service for converting various document formats to Markdown using Docling.

## Supported Formats

- **MS Office**: DOCX, XLSX, PPTX
- **PDF**: PDF files
- **Web**: HTML, XHTML
- **Data**: CSV
- **Markup**: Markdown, AsciiDoc

## Installation

```bash
uv sync
```

## Running the Server

Using the automated startup script (recommended):

```bash
uv run python scripts/start_backend.py
```

Or run this service individually with uvicorn:

```bash
uv run uvicorn backend.services.document_converter:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /
Root endpoint with API information

### GET /health
Health check endpoint

### POST /convert
Convert document to markdown

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (binary)

**Response:**
```json
{
  "success": true,
  "filename": "document.docx",
  "format": ".docx",
  "markdown": "# Converted markdown content..."
}
```

## Testing with Postman

1. Open Postman
2. Create a new POST request to `http://localhost:8000/convert`
3. Go to Body tab
4. Select "form-data"
5. Add a key named "file" and set type to "File"
6. Upload your document (DOCX, PDF, XLSX, etc.)
7. Send the request

## Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
