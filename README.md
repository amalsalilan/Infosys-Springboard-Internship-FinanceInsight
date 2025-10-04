# FinSight - Financial Document Analysis Platform

An AI-powered platform for comprehensive financial document analysis using sentiment analysis, named entity recognition, and structured information extraction.

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)
![React](https://img.shields.io/badge/React-18.3-61DAFB)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)

## Overview

FinSight provides three core analysis modules:

- **Sentiment Analysis** - Financial sentiment detection using FinBERT
- **Named Entity Recognition** - Entity extraction with inline type labels
- **LangExtract** - Custom structured information extraction using Google Gemini

## Key Features

- Multi-format document conversion (PDF, DOCX, XLSX, PPTX, HTML, CSV, Markdown)
- Real-time analysis with interactive visualizations
- Customizable extraction with example-based learning
- Navigation controls for extraction review
- Unicode and international character support

## Prerequisites

- Python 3.8+
- Node.js 16+
- Git

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd finsight

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install
```

### Running the Application

**Start Backend Services:**
```bash
python start_backend.py
```

Services will run on:
- Document Converter: `http://localhost:8000`
- Sentiment Analysis: `http://localhost:8001`
- NER Service: `http://localhost:8002`
- LangExtract: `http://localhost:8003`

**Start Frontend:**
```bash
npm run dev
```
Access at `http://localhost:8080`

### API Documentation

Interactive API documentation available at:
- `http://localhost:8000/docs` - Document Converter
- `http://localhost:8001/docs` - Sentiment Analysis
- `http://localhost:8002/docs` - NER Service
- `http://localhost:8003/docs` - LangExtract

## Architecture

### Technology Stack

**Backend:**
- FastAPI (Python)
- FinBERT (Sentiment Analysis)
- Transformers (NER)
- Google Gemini (LangExtract)
- Docling (Document Conversion)

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Recharts

### Services

| Service | Port | Endpoints |
|---------|------|-----------|
| Document Converter | 8000 | `/convert`, `/health` |
| Sentiment Analysis | 8001 | `/analyze`, `/health` |
| NER | 8002 | `/recognize`, `/health` |
| LangExtract | 8003 | `/extract`, `/health` |

## Project Structure

```
finsight/
├── backend/
│   ├── document_converter.py       # Document conversion service
│   ├── sentiment_service.py        # Sentiment analysis service
│   ├── ner_service.py              # NER service
│   ├── langextract_service.py      # LangExtract service
│   └── start_backend.py            # Unified startup script
├── src/
│   ├── components/                 # React components
│   │   ├── DocumentPreview.tsx
│   │   ├── InsightsPanel.tsx
│   │   ├── ExtractionsTable.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── ui/                     # shadcn/ui components
│   ├── services/
│   │   └── api.ts                  # API service layer
│   ├── pages/
│   │   └── Index.tsx               # Main page
│   └── main.tsx                    # Entry point
├── requirements.txt                # Python dependencies
├── package.json                    # Node dependencies
├── vite.config.ts                  # Vite configuration
└── README.md                       # This file
```

## Usage

1. Start all services (backend + frontend)
2. Navigate to `http://localhost:8080`
3. Select analysis type from sidebar
4. Upload document (PDF, DOCX, etc.)
5. Click "Process Document"
6. View results with visualizations

## Analysis Modules

### Sentiment Analysis
- Sentence-level classification (Positive/Negative/Neutral)
- FinBERT-powered financial sentiment detection
- Visual highlighting with confidence scores
- Distribution charts

### Named Entity Recognition
- Entity extraction with inline type labels
- Supported types: ORG, PER, LOC, MONEY, DATE, PERCENT
- Color-coded visualization
- Confidence scoring

### LangExtract
- Custom structured information extraction
- Google Gemini-powered
- Form Builder and JSON input modes
- Navigation controls for extraction review
- Example-based configuration

## Development

### Production Build
```bash
npm run build
npm run preview
```

### Troubleshooting

**Port conflicts:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

**Build errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## License

MIT License

## Acknowledgments

- FinBERT (ProsusAI)
- Hugging Face Transformers
- Docling
- LangExtract
- shadcn/ui
