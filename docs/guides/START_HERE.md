# 🚀 START HERE - FinSight Quick Start

## Step-by-Step Guide to Get Everything Running

### ✅ Step 1: Install uv and Python Dependencies

```bash
# Make sure you're in the project directory
cd "c:\Users\thefl\Documents\Code\internship\Batch 2\finsight"

# Install uv (if not already installed)
# Windows PowerShell:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install all Python dependencies with uv
uv sync
```

**Expected output**: Should install without errors.

---

### ✅ Step 2: Verify Node Dependencies

```bash
# Install Node.js dependencies (if not done already)
npm install
```

**Expected output**: Should complete successfully.

---

### ✅ Step 3: Start Backend Services

**Open a NEW terminal/command prompt** and run:

```bash
cd "c:\Users\thefl\Documents\Code\internship\Batch 2\finsight"
uv run python start_backend.py
```

**Expected output**:
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

Running services:
  • Document Converter: http://127.0.0.1:8000
  • Sentiment Analysis: http://127.0.0.1:8001
  • NER Service: http://127.0.0.1:8002
  • LangExtract Service: http://127.0.0.1:8003
```

**⚠️ IMPORTANT: Keep this terminal window OPEN!**

---

### ✅ Step 4: Test Document Converter (Optional but Recommended)

**Open another terminal** and run:

```bash
python test_converter.py
```

**Expected output**:
```
============================================================
Testing Document Converter
============================================================

📤 Sending request to http://localhost:8000/convert
📄 File: test_document.txt

📊 Response Status: 200

✅ Conversion successful!
   - Success: True
   - Filename: test_document.txt
   - Format: .txt

📝 Text extracted (XXX characters)
   Preview: Financial Report Q4 2023...

🌐 HTML generated (XXX characters)
   Preview: <!DOCTYPE html>...

💾 Saved files:
   ✅ text: output\test_document.txt
   ✅ markdown: output\test_document.md
   ✅ html: output\test_document.html

============================================================
✅ ALL TESTS PASSED!
============================================================
```

**If you see errors**:
- ❌ "Cannot connect to backend" → Backend not running (go back to Step 3)
- ❌ "ModuleNotFoundError" → Run `uv sync` (go back to Step 1)

---

### ✅ Step 5: Start Frontend

**Open ANOTHER terminal** (you should now have 2 terminals running) and run:

```bash
cd "c:\Users\thefl\Documents\Code\internship\Batch 2\finsight"
npm run dev
```

**Expected output**:
```
  VITE v5.4.19  ready in XXX ms

  ➜  Local:   http://localhost:8080/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**⚠️ IMPORTANT: Keep this terminal window OPEN too!**

---

### ✅ Step 6: Test the Application

1. **Open your browser** and go to: http://localhost:8080

2. **You should see**:
   - Sidebar with 3 analysis options
   - "Document Analysis" title
   - Upload button
   - Empty preview area

3. **Upload a document**:
   - Click the "Upload" button
   - Select any PDF, DOCX, or TXT file
   - **WAIT** 2-10 seconds

4. **You should see**:
   - ✅ Toast notification: "Document converted"
   - ✅ HTML preview appears in the center
   - ✅ Button changes to "Run Analysis"

5. **If preview is blank**:
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for any errors (should be none)
   - Go to Network tab
   - Look for `/convert` request (should be Status: 200)

---

## 🧪 Complete Workflow Test

### Test 1: Document Upload & Preview

1. Upload a document
2. ✅ HTML preview should appear automatically
3. ✅ No need to click anything!

### Test 2: Sentiment Analysis

1. Make sure "Sentiment Analysis" is selected in sidebar
2. Click "Run Analysis"
3. Wait 5-15 seconds
4. ✅ Preview updates with colored highlights
5. ✅ Pie chart appears on right
6. ✅ Table at bottom fills with results

### Test 3: Named Entity Recognition

1. Click "Named Entity Recognition" in sidebar
2. Click "Run Analysis"
3. Wait 5-15 seconds
4. ✅ Preview shows entity highlighting
5. ✅ Chart shows entity distribution
6. ✅ Table shows extracted entities

### Test 4: Language Extract

1. Click "Language Extract" in sidebar
2. Click "Run Analysis"
3. Wait 5-20 seconds
4. ✅ Visualization appears
5. ✅ Class breakdown shown
6. ✅ Table shows extractions

---

## 🐛 Troubleshooting

### Issue: Backend won't start

**Error**: `Port already in use`

**Solution**:
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then restart backend
uv run python start_backend.py
```

### Issue: Frontend shows blank page

**Solution**:
```bash
# Clear and reinstall
rmdir /s node_modules
del package-lock.json
npm install
npm run dev
```

### Issue: "Cannot connect" errors

**Checklist**:
- [ ] Backend terminal is still running?
- [ ] No errors in backend terminal?
- [ ] Can access http://localhost:8000/docs?
- [ ] Frontend terminal is still running?
- [ ] Browser on http://localhost:8080?

### Issue: Preview not showing

**Debug Steps**:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for errors
4. Go to Network tab
5. Upload document
6. Look for `/convert` request
7. Check if Status is 200
8. Click on request → Response tab
9. Verify HTML is returned

---

## 📁 What's Happening Behind the Scenes

### When you upload a document:

```
1. Browser → Frontend (React)
2. Frontend → POST /convert → Backend (Port 8000)
3. Backend uses Docling to convert document
4. Backend returns: { text, markdown, html }
5. Backend saves files to output/ folder
6. Frontend receives HTML
7. Frontend displays HTML in iframe
8. User sees preview!
```

### Saved files location:

```
finsight/
├── output/
│   ├── your_document.txt       ← Plain text
│   ├── your_document.md        ← Markdown
│   └── your_document.html      ← HTML (what you see in preview)
```

---

## ✅ Success Checklist

Before proceeding, make sure:

- [x] Backend terminal running (4 services on ports 8000-8003)
- [x] Frontend terminal running (port 8080)
- [x] Browser open at http://localhost:8080
- [x] No errors in either terminal
- [x] Can upload a document
- [x] HTML preview appears after upload
- [x] output/ folder contains converted files

---

## 🎯 Next Steps

Once basic preview is working:

1. ✅ Test all 3 analysis types
2. ✅ Try different file formats (PDF, DOCX, TXT)
3. ✅ Check that results appear in chart and table
4. ✅ Verify error handling (try invalid file)

---

## 📞 Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Check backend terminal for error messages
3. Check browser console (F12) for frontend errors
4. Verify all dependencies installed
5. Make sure both terminals are still running

---

## 🎉 You're Ready!

If you've completed all steps and tests pass, you have a **fully working** FinSight application!

**Key Features Working**:
- ✅ Document upload
- ✅ Automatic conversion
- ✅ HTML preview display
- ✅ Text/Markdown saved for later APIs
- ✅ Ready for analysis modules

**Now you can focus on testing and using the analysis features!** 🚀
