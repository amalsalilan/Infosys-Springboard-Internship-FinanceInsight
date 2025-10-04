# FinSight - Financial Document Analysis Platform

A comprehensive full-stack application for analyzing financial documents using AI-powered services including sentiment analysis, named entity recognition, and structured information extraction.

![FinSight Platform](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)
![React](https://img.shields.io/badge/React-18.3-61DAFB)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)

## 🚀 Features

### 📊 Core Capabilities
- **Document Conversion**: Converts various document formats (PDF, DOCX, XLSX, PPTX, HTML, CSV, Markdown) to text/markdown/HTML
- **Sentiment Analysis**: Analyzes financial sentiment using FinBERT with visual highlighting
- **Named Entity Recognition (NER)**: Identifies and extracts entities with inline type labels (ORG, LOC, PER, MONEY, DATE)
- **LangExtract**: Structured information extraction using Google Gemini with custom prompts and examples
- **Interactive Visualizations**: Real-time charts and insights for analysis results
- **Modern UI**: Built with React, TypeScript, Tailwind CSS, and shadcn/ui components

### ✨ Latest Enhancements (v1.1.0)
- ✅ **Auto-scaling Layout**: LangExtract bottom panel auto-scales with content (max-height: 70vh)
- ✅ **Navigation Controls**: Play/Previous/Next buttons for stepping through LangExtract extractions
- ✅ **Inline Entity Labels**: NER entities display with [TYPE] labels directly in text (removed legend)
- ✅ **Custom LangExtract Configuration**: Interactive dialog with Form Builder and JSON input modes
- ✅ **Fallback Examples**: Default contract-based examples when no user examples provided
- ✅ **Unicode Support**: Full support for special characters (✓, ✗, emojis, international text)
- ✅ **Improved Error Handling**: Specific error messages with actionable solutions
- ✅ **Fixed Layout**: Stable 400px top preview prevents squeezing on long documents

## 📋 Prerequisites

- Python 3.8+ (Python 3.13.7 recommended)
- Node.js 16+ and npm
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd finsight
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Backend Dependencies Include:
- FastAPI & Uvicorn (API framework)
- Docling (Document conversion)
- Transformers & PyTorch (AI models)
- BeautifulSoup4 (HTML processing)
- LangExtract (Structured extraction)
- httpx (Async HTTP client)

### 3. Frontend Setup

```bash
# Install Node dependencies
npm install
```

## 🚦 Running the Application

### Option 1: Automated Startup (Recommended)

#### Start Backend Services

```bash
python start_backend.py
```

This will start all 4 backend services:
- **Document Converter** → http://localhost:8000
- **Sentiment Analysis** → http://localhost:8001
- **NER Service** → http://localhost:8002
- **LangExtract Service** → http://localhost:8003

#### Start Frontend

In a separate terminal:

```bash
npm run dev
```

Frontend will be available at → http://localhost:8080

### Option 2: Manual Startup

Start each service individually:

```bash
# Terminal 1 - Document Converter
uvicorn document_converter:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Sentiment Analysis
uvicorn sentiment_service:app --host 127.0.0.1 --port 8001 --reload

# Terminal 3 - NER Service
uvicorn ner_service:app --host 127.0.0.1 --port 8002 --reload

# Terminal 4 - LangExtract Service
uvicorn langextract_service:app --host 127.0.0.1 --port 8003 --reload

# Terminal 5 - Frontend
npm run dev
```

## 📚 API Documentation

Once services are running, access interactive API docs:

- Document Converter: http://localhost:8000/docs
- Sentiment Analysis: http://localhost:8001/docs
- NER Service: http://localhost:8002/docs
- LangExtract Service: http://localhost:8003/docs

## 🏗️ Architecture

### Backend Services (FastAPI)

#### 1. Document Converter Service (Port 8000)
- Converts documents to markdown/text/HTML
- Supports: PDF, DOCX, XLSX, PPTX, HTML, CSV, Markdown, AsciiDoc
- Endpoints:
  - `POST /convert` - Convert document
  - `POST /convert-with-sentiment` - Convert + analyze sentiment
  - `GET /health` - Health check

#### 2. Sentiment Analysis Service (Port 8001)
- Financial sentiment analysis using FinBERT
- Sentence-level sentiment classification
- HTML highlighting with confidence-based colors
- Endpoints:
  - `POST /analyze` - Analyze sentiment
  - `GET /health` - Health check

#### 3. NER Service (Port 8002)
- Named Entity Recognition for financial documents
- Identifies: Organizations, People, Locations, Money, Dates, etc.
- Colored HTML visualization
- Endpoints:
  - `POST /recognize` - Recognize entities
  - `GET /visualization` - Get HTML visualization
  - `GET /health` - Health check

#### 4. LangExtract Service (Port 8003)
- Structured information extraction using LLMs
- Powered by Google Gemini
- Customizable extraction with examples
- Endpoints:
  - `POST /extract` - Extract information
  - `GET /visualization` - Get HTML visualization
  - `GET /health` - Health check

### Frontend (React + TypeScript)

#### Tech Stack:
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Recharts** - Data visualization
- **React Query** - API state management

#### Key Components:
- `Index.tsx` - Main page with document upload and analysis
- `DocumentPreview.tsx` - Document upload and preview
- `InsightsPanel.tsx` - Charts and analysis insights
- `ExtractionsTable.tsx` - Results table with extractions
- `Sidebar.tsx` - Analysis type selection
- `api.ts` - API service layer

## 🔧 Configuration

### Vite Proxy Configuration
The frontend uses Vite's proxy to forward API requests:
- `/api/converter/*` → http://localhost:8000
- `/api/sentiment/*` → http://localhost:8001
- `/api/ner/*` → http://localhost:8002
- `/api/langextract/*` → http://localhost:8003

### CORS Configuration
All backend services are configured to accept requests from:
- http://localhost:8080
- http://127.0.0.1:8080

## 📂 Project Structure

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

## 🎯 Usage

1. **Start all services** (backend + frontend)
2. **Open browser** → http://localhost:8080
3. **Select analysis type** from sidebar:
   - Sentiment Analysis
   - Named Entity Recognition
   - Language Extract
4. **Upload document** (PDF, DOCX, etc.)
5. **Click "Process Document"**
6. **View results**:
   - Highlighted HTML preview
   - Analysis charts/insights
   - Extractions table

## 🔍 Analysis Types

### Sentiment Analysis
- Classifies sentences as Positive, Negative, or Neutral
- Uses FinBERT (Financial BERT model)
- Visual highlighting with confidence scores
- Pie chart distribution
- Color-coded: 🟢 Green (Positive), 🔴 Red (Negative), ⚪ Gray (Neutral)

### Named Entity Recognition (NER)
- Identifies entities: People, Organizations, Locations, Money, Dates, Percent, etc.
- **Inline entity labels**: Text displays as `Beta Telecom [ORG]`, `New York [LOC]`, `$2,500,000 [MONEY]`
- Color-coded highlighting (no separate legend):
  - 🔵 Light Blue = Organization (ORG)
  - 🟢 Light Green = Location (LOC)
  - 🟠 Light Pink = Person (PER)
  - 💵 Pale Green = Money (MONEY)
  - 📅 Khaki = Date (DATE)
  - 📊 Peach = Percent (PERCENT)
- Entity distribution chart
- Confidence scores shown on hover

### LangExtract (Language Extract)
- Extracts structured information using Google Gemini
- **Interactive Configuration Dialog**:
  - Form Builder mode: Visual interface for building extraction config
  - JSON Input mode: Direct JSON configuration
  - Optional examples (auto-fallback to contract extraction)
- **Navigation Controls** (Play/Previous/Next):
  - Step through extractions with visual highlighting
  - Auto-scroll to current extraction in viewer
  - Counter shows position (e.g., "3 / 10")
- **Auto-scaling Visualization**:
  - Bottom panel grows with content (max 70vh)
  - Fixed top preview (400px) for stable layout
- Customizable extraction classes with attributes
- Example-based learning for accurate extraction

## 🐛 Troubleshooting

### Backend Issues

**Models not loading:**
```bash
# Models download on first run - be patient
# Check console for download progress
```

**Port already in use:**
```bash
# Kill process on port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port (macOS/Linux)
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**Build errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Ensure all backend services are running
- Check CORS configuration
- Verify proxy settings in vite.config.ts

## 📝 Development

### Build for Production

```bash
# Build frontend
npm run build

# Preview production build
npm run preview
```

### Linting

```bash
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FinBERT by ProsusAI for sentiment analysis
- Hugging Face Transformers for NER models
- Docling for document conversion
- LangExtract for structured extraction
- shadcn/ui for beautiful UI components
