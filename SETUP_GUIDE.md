# FinSight Setup Guide

## 🚀 Quick Setup (First Time)

Follow these steps to set up the project for the first time:

### Step 1: Install Backend Dependencies

```bash
# Make sure you're in the project directory
cd finsight

# Install Python dependencies
pip install -r requirements.txt
```

**Note**: This will install:
- FastAPI, Uvicorn
- Docling (document conversion)
- Transformers, PyTorch (AI models) - ~2GB download
- BeautifulSoup4, httpx, langextract

**First-time note**: AI model downloads happen on first run (FinBERT, NER model)

### Step 2: Install Frontend Dependencies

```bash
# Install Node.js dependencies
npm install
```

**Note**: This will install React, Vite, TypeScript, Tailwind, and UI libraries

### Step 3: Verify Installation

```bash
# Check Python packages
pip list | grep -E "fastapi|uvicorn|transformers|docling"

# Check Node packages
npm list --depth=0
```

## 🏃 Running the Application

### Option A: Automated (Recommended)

**Terminal 1 - Backend Services:**
```bash
python start_backend.py
```

Wait for all services to start (you'll see ✅ messages)

**Terminal 2 - Frontend:**
```bash
npm run dev
```

**Access the app**: http://localhost:8080

### Option B: Manual (For Debugging)

**Terminal 1 - Document Converter:**
```bash
uvicorn document_converter:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Sentiment Analysis:**
```bash
uvicorn sentiment_service:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 3 - NER Service:**
```bash
uvicorn ner_service:app --host 127.0.0.1 --port 8002 --reload
```

**Terminal 4 - LangExtract:**
```bash
uvicorn langextract_service:app --host 127.0.0.1 --port 8003 --reload
```

**Terminal 5 - Frontend:**
```bash
npm run dev
```

## 🧪 Testing the Integration

### Quick Test Flow:

1. **Open browser**: http://localhost:8080
2. **Select "Sentiment Analysis"** from sidebar
3. **Upload a document** (any .txt, .pdf, .docx file)
4. **Click "Process Document"**
5. **Verify**:
   - ✅ Document converts successfully
   - ✅ Sentiment analysis runs
   - ✅ Pie chart appears
   - ✅ Results table fills
   - ✅ HTML preview shows highlighted text

6. **Repeat for NER and LangExtract**

### Test Documents:

Create a test file `test.txt`:
```
Apple Inc. reported revenue of $394.3 billion for fiscal year 2022.
The company's CEO, Tim Cook, announced strong growth in Q4.
The headquarters in Cupertino, California saw record profits.
```

## 🐛 Common Issues & Solutions

### Issue 1: Port Already in Use
**Error**: `Address already in use`

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue 2: Python Module Not Found
**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue 3: Models Not Loading
**Error**: `Model not loaded`

**Solution**:
- First run downloads models (~2GB for transformers)
- Be patient, check console for progress
- Ensure stable internet connection

### Issue 4: CORS Error in Browser
**Error**: `CORS policy: No 'Access-Control-Allow-Origin'`

**Solution**:
- Verify backend services are running
- Check CORS middleware in Python files
- Restart backend services

### Issue 5: Frontend Build Errors
**Error**: `Cannot find module '@/services/api'`

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue 6: LangExtract API Key Error
**Error**: `LANGEXTRACT_API_KEY not set`

**Solution**:
- API key is hardcoded in `langextract_service.py`
- For production, use environment variables
- Current key: `AIzaSyCJH2lOrks1C_faZxubvEYAIb2rw7yHIV8`

## 📊 Service Health Check

Verify all services are running:

```bash
# Check each service
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "service-name",
  "model_loaded": true
}
```

## 🔍 API Documentation

Once services are running, access interactive docs:

- **Document Converter**: http://localhost:8000/docs
- **Sentiment Analysis**: http://localhost:8001/docs
- **NER Service**: http://localhost:8002/docs
- **LangExtract**: http://localhost:8003/docs

## 📁 Project Checklist

Before running, ensure you have:

- [x] Python 3.8+ installed
- [x] Node.js 16+ installed
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] Frontend packages installed (`npm install`)
- [x] At least 5GB free disk space (for models)
- [x] Stable internet connection (for first run)

## 🎯 Success Indicators

You'll know it's working when:

1. ✅ Backend startup shows all 4 services running
2. ✅ Frontend shows at http://localhost:8080
3. ✅ No console errors in browser
4. ✅ Document upload works
5. ✅ Processing completes successfully
6. ✅ Charts and tables populate with data

## 🔄 Stopping the Application

**Automated Setup**:
- Press `Ctrl+C` in both terminals
- Backend script will gracefully shutdown all services

**Manual Setup**:
- Press `Ctrl+C` in each terminal window

## 📝 Development Mode

For development with hot reload:

```bash
# Backend with auto-reload (already enabled in startup script)
python start_backend.py

# Frontend with hot reload
npm run dev
```

Changes to React components will hot-reload automatically.
Changes to Python files will trigger service restart.

## 🚢 Production Build

```bash
# Build frontend for production
npm run build

# Serve production build
npm run preview
```

Production build will be in `dist/` folder.

## 💡 Pro Tips

1. **Use the automated startup** - It's faster and cleaner
2. **Keep terminals visible** - Watch for errors in real-time
3. **Test one analysis type at a time** - Easier to debug
4. **Check browser console** - For frontend errors
5. **Use API docs** - Test endpoints directly
6. **Start small** - Test with simple text files first

## 🎉 You're Ready!

If you've followed these steps, your FinSight application should be fully operational!

Next steps:
- Upload a document
- Try all 3 analysis types
- Explore the visualizations
- Check the API documentation

Happy analyzing! 🚀
