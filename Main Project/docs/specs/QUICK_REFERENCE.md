# FinSight Quick Reference

## 🚀 Quick Start Commands

### First Time Setup
```bash
# Install uv (Python package manager)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync
npm install
```

### Run Application
```bash
# Terminal 1
uv run python start_backend.py

# Terminal 2
npm run dev
```

### Access
- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs (8001, 8002, 8003)

## 🔌 Service Ports

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Document Converter | 8000 | http://localhost:8000 | Convert documents |
| Sentiment Analysis | 8001 | http://localhost:8001 | Analyze sentiment |
| NER Service | 8002 | http://localhost:8002 | Extract entities |
| LangExtract | 8003 | http://localhost:8003 | Structured extraction |
| Frontend | 8080 | http://localhost:8080 | User interface |

## 📋 API Endpoints Reference

### Document Converter (8000)
```
POST /convert                    # Convert document
POST /convert-with-sentiment     # Convert + sentiment
GET  /health                     # Health check
```

### Sentiment Analysis (8001)
```
POST /analyze                    # Analyze sentiment
GET  /health                     # Health check
```

### NER Service (8002)
```
POST /recognize                  # Recognize entities
GET  /visualization              # Get HTML viz
GET  /health                     # Health check
```

### LangExtract (8003)
```
POST /extract                    # Extract information
GET  /visualization              # Get HTML viz
GET  /health                     # Health check
```

## 🎯 Analysis Types

### Sentiment Analysis
- **Input**: Text/Document
- **Output**: Positive/Negative/Neutral classification
- **Visualization**: Pie chart + highlighted HTML
- **Use Case**: Financial report sentiment

### Named Entity Recognition
- **Input**: Text/Document
- **Output**: Entities (Person, Org, Location, Money, Date)
- **Visualization**: Entity chart + highlighted HTML
- **Use Case**: Extract companies, people, amounts

### Language Extract
- **Input**: Text/Document + Examples
- **Output**: Structured extractions
- **Visualization**: Class breakdown + HTML
- **Use Case**: Custom entity extraction

## 📁 File Structure

```
finsight/
├── Python Services
│   ├── document_converter.py
│   ├── sentiment_service.py
│   ├── ner_service.py
│   ├── langextract_service.py
│   └── start_backend.py
│
├── Frontend
│   ├── src/
│   │   ├── pages/Index.tsx
│   │   ├── components/
│   │   │   ├── DocumentPreview.tsx
│   │   │   ├── InsightsPanel.tsx
│   │   │   └── ExtractionsTable.tsx
│   │   └── services/api.ts
│   └── vite.config.ts
│
└── Config Files
    ├── requirements.txt
    ├── package.json
    └── README.md
```

## 🔧 Common Commands

### Backend
```bash
# Start all services
uv run python start_backend.py

# Individual service
uv run uvicorn sentiment_service:app --port 8001 --reload

# Check health
curl http://localhost:8001/health
```

### Frontend
```bash
# Development
npm run dev

# Build
npm run build

# Preview
npm run preview

# Lint
npm run lint
```

### Dependencies
```bash
# Python
uv sync
uv pip list

# Node
npm install
npm list --depth=0
```

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `taskkill /PID <PID> /F` (Windows)<br>`lsof -ti:8000 \| xargs kill -9` (Mac/Linux) |
| Module not found | `uv sync` |
| CORS error | Restart backend services |
| Build error | `rm -rf node_modules && npm install` |
| Model not loading | Wait for download, check internet |

## 🎨 UI Components

### Main Page (Index.tsx)
- Document upload
- Analysis type selection
- Process button
- Results display

### Sidebar
- Sentiment Analysis
- Named Entity Recognition
- Language Extract

### Document Preview
- Upload button
- File display
- HTML preview
- Clear button

### Insights Panel
- Dynamic charts
- Analysis metrics
- Real-time updates

### Extractions Table
- Results display
- Color-coded classes
- Confidence scores

## 📊 Data Flow

```
Upload → Convert → Analyze → Visualize

1. User uploads document
2. Frontend sends to Document Converter
3. Converter returns text/HTML
4. Frontend sends to Analysis Service
5. Service returns results
6. Frontend displays charts + table
```

## 🔑 Environment Variables

```bash
# Google Gemini API Key (for LangExtract)
# Using uv
uv run --env GEMINI_API_KEY=your_key python start_backend.py

# Or create .env file
echo "GEMINI_API_KEY=your_key" > .env
```

## 📦 Dependencies

### Python
- fastapi >= 0.115.5
- uvicorn >= 0.32.1
- docling >= 2.15.0
- transformers >= 4.30.0
- torch >= 2.0.0
- beautifulsoup4 >= 4.12.0
- langextract >= 0.1.0
- httpx >= 0.24.0

### Node
- react ^18.3.1
- typescript ^5.8.3
- vite ^5.4.19
- tailwindcss ^3.4.17
- recharts ^2.15.4

## 🧪 Test Workflow

1. Start backend: `uv run python start_backend.py`
2. Start frontend: `npm run dev`
3. Open: http://localhost:8080
4. Upload: test.txt (or any doc)
5. Select: Sentiment Analysis
6. Click: Process Document
7. Verify: Chart + Table + Preview
8. Repeat for NER and LangExtract

## 📝 Code Snippets

### API Call (TypeScript)
```typescript
import { processDocument } from '@/services/api';

const result = await processDocument(file, 'sentiment');
console.log(result.analysis);
```

### Health Check (Python)
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### CORS Setup (Python)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 Supported File Types

- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)
- PowerPoint (.pptx)
- HTML (.html)
- CSV (.csv)
- Markdown (.md)
- Text (.txt)

## 🔗 Useful Links

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Recharts](https://recharts.org/)

## 💡 Pro Tips

1. Always start backend before frontend
2. Check `/health` endpoints to verify services
3. Use API docs (`/docs`) for testing
4. Monitor console for errors
5. Clear browser cache if issues persist
6. Use the automated startup script
7. Test with small files first

## 🚨 Important Notes

- First run downloads AI models (~2GB)
- LangExtract requires API key
- CORS configured for localhost only
- All data saved to `output/` folder
- Frontend proxy handles API routing

---

**Need Help?** Check README.md or SETUP_GUIDE.md for detailed instructions.
