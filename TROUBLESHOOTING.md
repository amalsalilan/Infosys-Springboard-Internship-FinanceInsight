# Troubleshooting Guide - FinSight

## Issue: Document Processing Stuck on "Processing..."

### Symptoms:
- Upload a document
- Click "Process Document"
- Shows "Processing..." indefinitely
- No results appear
- Preview area remains empty

### Root Cause:
**Backend services are not running!**

### Solution:

#### Step 1: Check if Backend is Running

Open a command prompt and check if services are running:

```bash
# Check Document Converter
curl http://localhost:8000/health

# Check Sentiment Service
curl http://localhost:8001/health

# Check NER Service
curl http://localhost:8002/health

# Check LangExtract Service
curl http://localhost:8003/health
```

If you get errors like "Connection refused" or "Failed to connect", the backend is **NOT running**.

#### Step 2: Start Backend Services

**Open a NEW terminal/command prompt** and run:

```bash
python start_backend.py
```

You should see output like:
```
============================================================
Starting FinSight Backend Services
============================================================

🚀 Starting Document Converter on http://127.0.0.1:8000
🚀 Starting Sentiment Analysis on http://127.0.0.1:8001
🚀 Starting NER Service on http://127.0.0.1:8002
🚀 Starting LangExtract Service on http://127.0.0.1:8003

============================================================
✅ All services started successfully!
============================================================
```

**IMPORTANT**: Keep this terminal window open! The services need to keep running.

#### Step 3: Verify Frontend is Running

Make sure your frontend is also running in a **SEPARATE terminal**:

```bash
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:8080/
```

#### Step 4: Test Again

1. Go to http://localhost:8080
2. Upload a document
3. Click "Process Document"
4. Results should appear within 5-30 seconds

---

## Issue: HTML Preview Not Rendering

### Symptoms:
- Processing completes successfully
- Table shows extractions
- But preview area is blank/white

### Possible Causes & Solutions:

#### Cause 1: HTML Content is Empty

**Check browser console** (F12 → Console tab) for errors like:
- `Failed to fetch`
- `CORS error`
- `Network error`

**Solution**: Restart backend services

#### Cause 2: Iframe Sandbox Restrictions

The iframe needs proper permissions.

**Check**: Open `src/components/DocumentPreview.tsx` line 37:
```tsx
sandbox="allow-same-origin"
```

Should be present. If missing, add it.

#### Cause 3: Invalid HTML Content

The backend might be returning invalid HTML.

**Test directly**:
```bash
# Test document conversion
curl -X POST http://localhost:8000/convert \
  -F "file=@path/to/test.pdf"
```

Check if response contains valid HTML.

---

## Issue: CORS Errors in Browser Console

### Symptoms:
Browser console shows:
```
Access to fetch at 'http://localhost:8000/convert' from origin 'http://localhost:8080'
has been blocked by CORS policy
```

### Solution:

#### Step 1: Verify CORS Configuration

Check each backend service file has CORS middleware:

**In `document_converter.py`, `sentiment_service.py`, `ner_service.py`, `langextract_service.py`:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Step 2: Restart Backend

CORS changes require restart:
```bash
# Stop backend (Ctrl+C)
# Start again
python start_backend.py
```

---

## Issue: "Module Not Found" Errors

### Symptoms:
```
ModuleNotFoundError: No module named 'fastapi'
ModuleNotFoundError: No module named 'transformers'
```

### Solution:

```bash
# Make sure you're in the project directory
cd finsight

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - fastapi
# - uvicorn
# - docling
# - transformers
# - torch
# - beautifulsoup4
# - langextract
# - httpx
```

---

## Issue: Port Already in Use

### Symptoms:
```
ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000):
only one usage of each socket address (protocol/network address/port) is normally permitted
```

### Solution:

**Windows:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

Then restart the backend services.

---

## Issue: Models Not Loading / Taking Forever

### Symptoms:
- Backend starts but processing never completes
- Console shows "Loading model..."
- First time running sentiment or NER analysis

### Explanation:
**This is NORMAL on first run!** The AI models need to download (~2GB).

### Solution:

**Be patient!** Models download only once:
- FinBERT (sentiment): ~500MB
- BERT NER model: ~400MB
- Other dependencies: ~1GB

**Monitor progress** in the backend terminal. You'll see:
```
Downloading model...
Loading FinBERT model...
FinBERT model loaded successfully!
```

**Subsequent runs** will be instant (models are cached).

---

## Issue: Frontend Build Errors

### Symptoms:
```
Cannot find module '@/services/api'
Type error: ... has no exported member
```

### Solution:

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Or on Windows
rmdir /s node_modules
del package-lock.json
npm install
```

---

## Issue: Blank Screen / White Page

### Symptoms:
- Frontend URL loads but shows nothing
- Completely blank page

### Solution:

#### Step 1: Check Browser Console
Press F12 → Console tab

Look for JavaScript errors.

#### Step 2: Hard Refresh
- Chrome/Edge: Ctrl+Shift+R
- Firefox: Ctrl+F5
- Clear browser cache

#### Step 3: Rebuild Frontend
```bash
npm run build
npm run dev
```

---

## Quick Diagnostic Checklist

Run through this checklist:

- [ ] Backend services running? (`python start_backend.py`)
- [ ] Frontend running? (`npm run dev`)
- [ ] Can access http://localhost:8080?
- [ ] Can access http://localhost:8000/docs?
- [ ] Browser console shows no errors? (F12)
- [ ] Network tab shows API calls? (F12 → Network)
- [ ] Both terminals still open and active?

---

## Still Not Working?

### Get Detailed Error Information:

1. **Open Browser DevTools** (F12)
2. **Go to Network tab**
3. **Try processing a document**
4. **Click on failed requests** (red ones)
5. **Check Response tab** for error details

### Check Backend Logs:

Look at the terminal running `start_backend.py` for errors like:
- `404 Not Found`
- `500 Internal Server Error`
- Python traceback/exception details

### Test Backend Directly:

```bash
# Test document conversion
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.txt"

# Test sentiment analysis
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"This is great news!","html":null}'
```

---

## Common Workflow Issues

### Issue: Switching Analysis Types Doesn't Work

**Solution**: Click "Clear" button before switching analysis types, then upload document again.

### Issue: Results from Previous Analysis Showing

**Solution**: Always click "Clear" before processing a new document.

### Issue: Can't Upload PDF Files

**Solution**: Check file size. Very large PDFs (>50MB) may timeout. Try a smaller file first.

---

## Getting Help

If issues persist:

1. Check `README.md` for setup instructions
2. Check `SETUP_GUIDE.md` for detailed setup
3. Verify all files in `INTEGRATION_SUMMARY.md` are present
4. Create an issue with:
   - Error messages from browser console
   - Error messages from backend terminal
   - Steps to reproduce
   - OS and browser version

---

## Emergency Reset

If everything is broken:

```bash
# Stop all services (Ctrl+C in all terminals)

# Backend reset
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# Frontend reset
rm -rf node_modules package-lock.json
npm install

# Start fresh
python start_backend.py  # Terminal 1
npm run dev              # Terminal 2
```

This should fix 99% of issues!
