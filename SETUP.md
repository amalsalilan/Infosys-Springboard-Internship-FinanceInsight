# FinSight - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Environment Setup](#environment-setup)
4. [Running the Application](#running-the-application)
5. [Verification](#verification)
6. [Common Issues](#common-issues)

---

## Prerequisites

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher (3.11+ recommended)
- **uv**: Latest version (Python package manager)
- **Node.js**: 16.0 or higher (22.x recommended)
- **Git**: Latest version
- **RAM**: Minimum 8GB (16GB recommended for ML models)
- **Disk Space**: At least 5GB free space

### Required Tools

#### 1. uv (Python Package Manager)

`uv` is a fast Python package installer and resolver that manages virtual environments and dependencies.

**Windows:**
```powershell
# Install uv using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
# Install uv using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify installation:**
```bash
uv --version
```

#### 2. Node.js 16+
**Windows/macOS:**
- Download from [nodejs.org](https://nodejs.org/)
- Install LTS version

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
```

#### 3. Git
**Windows:**
- Download from [git-scm.com](https://git-scm.com/)

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

---

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/amalsalilan/shiny-meme.git

# Navigate to project directory
cd shiny-meme
```

### Step 2: Python Environment Setup with uv

#### Sync Dependencies and Create Virtual Environment

`uv` automatically creates and manages virtual environments for you.

```bash
# Install all Python dependencies (creates .venv automatically)
uv sync
```

This single command will:
- Create a virtual environment in `.venv/`
- Install all packages from `requirements.txt`
- Lock dependencies for reproducibility

**Packages installed:**
- `fastapi==0.115.5` - Web framework for backend services
- `uvicorn[standard]==0.32.1` - ASGI server
- `python-multipart==0.0.20` - File upload support
- `docling==2.15.0` - Document conversion library
- `transformers>=4.30.0` - Hugging Face transformers for NLP
- `torch>=2.0.0` - PyTorch for ML models
- `beautifulsoup4>=4.12.0` - HTML parsing
- `langextract>=0.1.0` - Structured information extraction
- `httpx>=0.24.0` - HTTP client

### Step 3: Node.js Dependencies

```bash
# Install frontend dependencies
npm install
```

**This installs:**
- React 18.3 with TypeScript
- Vite build tool
- Tailwind CSS + shadcn/ui components
- React Router, React Query
- Recharts for visualizations
- All UI component libraries

---

## Environment Setup

### Required API Keys

#### Google Gemini API Key (for LangExtract)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set environment variable using `uv`:

```bash
# Set API key using uv (recommended)
uv run --env GEMINI_API_KEY=your_actual_api_key_here python start_backend.py
```

**Or create a `.env` file** in the project root:

```bash
# Windows
echo GEMINI_API_KEY=your_api_key_here > .env

# macOS/Linux
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

`.env` file format:
```
GEMINI_API_KEY=your_actual_api_key_here
```

**Note:** `uv` will automatically load `.env` files when running commands.

### Verify Installation

```bash
# Check installed Python packages
uv pip list

# Check Node packages
npm list --depth=0
```

---

## Running the Application

### Method 1: Using uv (Recommended)

#### Start Backend Services

```bash
# Run backend with uv (auto-activates environment)
uv run python start_backend.py
```

This will start 4 services:
- **Document Converter**: http://localhost:8000
- **Sentiment Analysis**: http://localhost:8001
- **NER Service**: http://localhost:8002
- **LangExtract**: http://localhost:8003

#### Start Frontend

Open a **new terminal** window:

```bash
# Start development server
npm run dev
```

Frontend will be available at: http://localhost:8080

### Method 2: Manual Service Startup with uv

If you need to run services individually:

**Terminal 1 - Document Converter:**
```bash
uv run uvicorn document_converter:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Sentiment Analysis:**
```bash
uv run uvicorn sentiment_service:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 3 - NER Service:**
```bash
uv run uvicorn ner_service:app --host 127.0.0.1 --port 8002 --reload
```

**Terminal 4 - LangExtract:**
```bash
uv run uvicorn langextract_service:app --host 127.0.0.1 --port 8003 --reload
```

**Terminal 5 - Frontend:**
```bash
npm run dev
```

---

## Verification

### 1. Check Backend Services

Visit these URLs in your browser:
- http://localhost:8000/health - Document Converter health check
- http://localhost:8001/health - Sentiment Analysis health check
- http://localhost:8002/health - NER Service health check
- http://localhost:8003/health - LangExtract health check

All should return: `{"status": "healthy"}`

### 2. Check API Documentation

Interactive API docs (Swagger UI):
- http://localhost:8000/docs - Document Converter
- http://localhost:8001/docs - Sentiment Analysis
- http://localhost:8002/docs - NER Service
- http://localhost:8003/docs - LangExtract

### 3. Check Frontend

Visit http://localhost:8080
- You should see the FinSight interface
- Sidebar with analysis options
- Document upload area

### 4. Test Full Workflow

1. Navigate to http://localhost:8080
2. Select "Sentiment Analysis" from sidebar
3. Upload a sample text file or PDF
4. Click "Process Document"
5. Verify results display correctly

---

## Common Issues

### Port Already in Use

**Error:** `Address already in use`

**Windows Solution:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

**macOS/Linux Solution:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Python Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Reinstall dependencies with uv
uv sync
```

### Node Modules Issues

**Error:** `Cannot find module` or build errors

**Solution:**
```bash
# Remove existing installations
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### PyTorch Installation Issues

**Error:** `torch` installation fails or is slow

**Solution (CPU-only, faster):**
```bash
# Install PyTorch CPU version with uv
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### CORS Errors in Browser

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
- Ensure backend services are running
- Check that API URLs in `src/services/api.ts` match your setup
- Default: `http://localhost:8000`, `http://localhost:8001`, etc.

### Frontend Not Loading

**Check:**
1. Backend services are running (check health endpoints)
2. No console errors in browser DevTools (F12)
3. Correct port (http://localhost:8080, not 5173)

**Vite Config:**
The `vite.config.ts` is configured to run on port 8080:
```typescript
server: {
  port: 8080,
  host: "::",
  strictPort: false,
}
```

### Environment Variables Not Loading

**Error:** API key not found or authentication errors

**Solution:**
```bash
# Option 1: Use uv with --env flag
uv run --env GEMINI_API_KEY=your_key python start_backend.py

# Option 2: Ensure .env file exists and is properly formatted
cat .env  # macOS/Linux
type .env # Windows

# Option 3: Export manually before running
export GEMINI_API_KEY=your_key  # macOS/Linux
set GEMINI_API_KEY=your_key     # Windows CMD
$env:GEMINI_API_KEY="your_key"  # Windows PowerShell
```

---

## Production Build

### Build Frontend for Production

```bash
# Create optimized build
npm run build

# Preview production build
npm run preview
```

Build output will be in `dist/` directory.

### Run Backend in Production Mode

```bash
# Without --reload flag for better performance
uv run uvicorn document_converter:app --host 0.0.0.0 --port 8000
```

---

## Architecture Overview

### Backend Services (Python/FastAPI)
```
┌─────────────────────────────────────────┐
│         FinSight Backend Services       │
├─────────────────────────────────────────┤
│  Port 8000: Document Converter          │
│  - Converts PDF, DOCX, XLSX → Markdown  │
│  - Uses: docling library                │
├─────────────────────────────────────────┤
│  Port 8001: Sentiment Analysis          │
│  - FinBERT model for financial sentiment│
│  - Returns: Positive/Negative/Neutral   │
├─────────────────────────────────────────┤
│  Port 8002: Named Entity Recognition    │
│  - Extracts entities from text          │
│  - Types: ORG, PER, LOC, MONEY, etc.    │
├─────────────────────────────────────────┤
│  Port 8003: LangExtract                 │
│  - Custom structured data extraction    │
│  - Uses: Google Gemini API              │
└─────────────────────────────────────────┘
```

### Frontend (React/TypeScript)
```
┌─────────────────────────────────────────┐
│        FinSight Frontend (React)        │
├─────────────────────────────────────────┤
│  Framework: React 18 + TypeScript       │
│  Build Tool: Vite                       │
│  UI: Tailwind CSS + shadcn/ui           │
│  Charts: Recharts                       │
│  Routing: React Router                  │
│  API: React Query + Fetch               │
└─────────────────────────────────────────┘
```

### Data Flow
```
User Upload → Document Converter → Selected Analysis Service
                                          ↓
                                    Process Document
                                          ↓
                              Return Results (JSON)
                                          ↓
                              Frontend Visualization
```

---

## Next Steps

After successful setup:

1. **Explore Analysis Features**
   - Try Sentiment Analysis on financial documents
   - Test NER on company reports
   - Create custom extraction schemas with LangExtract

2. **Review Documentation**
   - `README.md` - Project overview
   - `CHANGELOG.md` - Version history
   - API docs at `/docs` endpoints

3. **Development**
   - Frontend code: `src/` directory
   - Backend services: Root directory (`*_service.py`)
   - Components: `src/components/`

---

## Support

For issues or questions:
- Check existing documentation files
- Review API documentation at service `/docs` endpoints
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if it exists

---

## Quick Command Reference

```bash
# Install/sync all Python dependencies
uv sync

# Run Python scripts with uv
uv run python script.py

# Start all backend services
uv run python start_backend.py

# Install new Python package
uv pip install package-name

# Add package to requirements.txt
uv pip freeze > requirements.txt

# Run with environment variable
uv run --env KEY=value python script.py

# List installed packages
uv pip list

# Start frontend
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Install new Node package
npm install package-name
```

---

## uv Benefits

- **Fast**: 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution
- **Simple**: No need to manually activate virtual environments
- **Integrated**: Automatic `.env` file loading
- **Modern**: Built in Rust for performance

---

**Last Updated:** October 2025
**FinSight Version:** 1.0.0
