# Complete Workflow Guide - FinSight

## 📊 End-to-End Workflow

### Overview
This document explains the complete workflow from document upload to result visualization.

---

## 🔄 Automatic Workflow (Optimized)

### Step 1: Document Upload → Automatic Conversion
**User Action**: Upload document via "Upload" button

**What Happens Automatically**:
1. ✅ File is validated (PDF, DOCX, TXT, etc.)
2. ✅ Document sent to **Document Converter Service** (Port 8000)
3. ✅ Converter extracts:
   - Plain text
   - Markdown format
   - HTML representation
4. ✅ HTML preview **immediately displayed** in preview pane
5. ✅ User sees toast: "Document converted"

**Technical Flow**:
```
User uploads file
    ↓
handleFileUpload() triggered
    ↓
POST /convert to localhost:8000
    ↓
Document Converter processes file
    ↓
Returns: { text, markdown, html }
    ↓
setConversionData() stores result
    ↓
setHtmlPreview() displays HTML
    ↓
Toast notification shown
```

**API Endpoint**: `POST http://localhost:8000/convert`

**Request**:
```
FormData {
  file: <uploaded file>
}
```

**Response**:
```json
{
  "success": true,
  "filename": "document.pdf",
  "format": ".pdf",
  "markdown": "...",
  "text": "...",
  "html": "<!DOCTYPE html>..."
}
```

---

### Step 2: Analysis Selection
**User Action**: Select analysis type from sidebar

**Options**:
1. **Sentiment Analysis** - Classify text as positive/negative/neutral
2. **Named Entity Recognition** - Extract entities (people, orgs, locations)
3. **Language Extract** - Custom structured extraction

**What Happens**:
- `selectedAnalysis` state updated
- No API call yet (waiting for user to click "Run Analysis")
- Existing HTML preview remains visible

---

### Step 3: Analysis Execution
**User Action**: Click "Run Analysis" button

**What Happens** (Optimized - No Re-conversion):
1. ✅ System checks if document already converted
2. ✅ If yes, **reuses existing conversion** (no duplicate API call!)
3. ✅ Sends converted text to selected analysis service
4. ✅ Analysis service processes text
5. ✅ Results displayed:
   - **Preview**: Updated HTML with highlighting
   - **Insights**: Chart with distribution
   - **Table**: Detailed extractions

**Technical Flow**:

#### For Sentiment Analysis:
```
User clicks "Run Analysis"
    ↓
handleProcess() triggered
    ↓
Check if conversionData exists (YES)
    ↓
Use existing conversion.text + conversion.html
    ↓
POST /analyze to localhost:8001
    ↓
Sentiment Service analyzes with FinBERT
    ↓
Returns: { sentiment_results[], highlighted_html }
    ↓
setAnalysisResults() stores results
    ↓
setHtmlPreview() updates with highlighted HTML
    ↓
setExtractions() populates table
    ↓
Chart rendered with distribution
```

**API Endpoint**: `POST http://localhost:8001/analyze`

**Request**:
```json
{
  "text": "extracted text from document",
  "html": "<!DOCTYPE html>..."
}
```

**Response**:
```json
{
  "sentiment_results": [
    {
      "sentence": "This is great news!",
      "class": "positive",
      "position": { "start": 0, "end": 19 },
      "confidence_scores": {
        "positive": 0.95,
        "negative": 0.03,
        "neutral": 0.02
      }
    }
  ],
  "highlighted_html": "<!DOCTYPE html>..."
}
```

#### For Named Entity Recognition:
```
User clicks "Run Analysis"
    ↓
handleProcess() triggered
    ↓
Use existing conversion.text
    ↓
POST /recognize to localhost:8002
    ↓
NER Service extracts entities
    ↓
Returns: { entities[], highlighted_html }
    ↓
Results displayed
```

**API Endpoint**: `POST http://localhost:8002/recognize`

**Request**:
```json
{
  "text": "Apple Inc. reported revenue of $394.3 billion."
}
```

**Response**:
```json
{
  "success": true,
  "entities": [
    {
      "entity_group": "ORG",
      "score": 0.9987,
      "word": "Apple Inc.",
      "start": 0,
      "end": 10
    },
    {
      "entity_group": "MONEY",
      "score": 0.9876,
      "word": "$394.3 billion",
      "start": 30,
      "end": 44
    }
  ],
  "highlighted_html": "<!DOCTYPE html>..."
}
```

#### For Language Extract:
```
User clicks "Run Analysis"
    ↓
handleProcess() triggered
    ↓
Use existing conversion.text
    ↓
POST /extract to localhost:8003
    ↓
LangExtract uses Gemini AI
    ↓
Returns: { extractions[], html_visualization }
    ↓
Results displayed
```

**API Endpoint**: `POST http://localhost:8003/extract`

**Request**:
```json
{
  "text": "document text",
  "prompt_description": "Extract financial entities...",
  "examples": [...],
  "model_id": "gemini-2.0-flash-exp"
}
```

**Response**:
```json
{
  "success": true,
  "extractions": [
    {
      "extraction_class": "Company",
      "extraction_text": "Apple Inc.",
      "attributes": { "type": "organization" },
      "start_char": 0,
      "end_char": 10
    }
  ],
  "html_visualization": "<!DOCTYPE html>..."
}
```

---

## 🎨 UI State Management

### States During Workflow:

| Stage | Button Text | Preview State | Table State | Chart State |
|-------|------------|---------------|-------------|-------------|
| **No document** | "Process Document" (disabled) | Empty placeholder | Empty | Empty |
| **Uploading** | "Converting..." | Loading | Empty | Empty |
| **Converted** | "Run Analysis" | **HTML visible** | Empty | Empty |
| **Analyzing** | "Analyzing..." | HTML visible | Empty | Empty |
| **Complete** | "Run Analysis" | **Highlighted HTML** | **Filled** | **Rendered** |

### Loading Indicators:
- `isConverting`: During document conversion
- `isProcessing`: During analysis
- Button disabled when either is true
- Button text changes based on state

---

## 🔄 State Variables Explained

### Frontend State (Index.tsx):

```typescript
const [document, setDocument] = useState<File | null>(null);
// Stores the uploaded file object

const [conversionData, setConversionData] = useState<ConversionResponse | null>(null);
// Stores conversion result (text, markdown, html)
// Used to avoid re-converting document

const [htmlPreview, setHtmlPreview] = useState<string | null>(null);
// HTML to display in preview iframe
// Updates from conversion.html → highlighted_html

const [analysisResults, setAnalysisResults] = useState<...>(null);
// Stores full analysis results from backend
// Type changes based on selectedAnalysis

const [extractions, setExtractions] = useState<Array<...>>([]);
// Formatted data for table display
// Derived from analysisResults

const [isConverting, setIsConverting] = useState(false);
// True during document conversion

const [isProcessing, setIsProcessing] = useState(false);
// True during analysis

const [selectedAnalysis, setSelectedAnalysis] = useState<...>("sentiment");
// Current analysis type selection
```

---

## 🎯 Optimization Details

### 1. **No Double Conversion**
- Document converted ONCE on upload
- Conversion result cached in `conversionData`
- All analyses reuse the same converted text
- **Saves time and API calls!**

### 2. **Immediate Preview**
- HTML shown immediately after upload
- User can see document content before analysis
- Better UX - no waiting

### 3. **Lazy Analysis**
- Analysis only runs when user clicks button
- User can review preview first
- Can switch analysis types without re-upload

---

## 🧪 Testing Each Workflow

### Test 1: Sentiment Analysis Flow

**Steps**:
1. Start backend: `python start_backend.py`
2. Start frontend: `npm run dev`
3. Open http://localhost:8080
4. Click "Upload" → Select a PDF/TXT file
5. **Verify**: HTML preview appears within 2-5 seconds
6. **Verify**: Toast shows "Document converted"
7. Ensure "Sentiment Analysis" selected in sidebar
8. Click "Run Analysis"
9. **Verify**: Button shows "Analyzing..."
10. **Verify** (after 5-10 sec):
    - Preview shows highlighted text (green/red/gray)
    - Pie chart shows positive/negative/neutral %
    - Table shows sentences with sentiment class
    - Insights show counts

**Expected Results**:
- ✅ Green highlights for positive sentences
- ✅ Red highlights for negative sentences
- ✅ Gray highlights for neutral sentences
- ✅ Pie chart with 3 sections
- ✅ Table with sentence + class + confidence %

---

### Test 2: NER Flow

**Steps**:
1. Upload document (auto-converts, shows preview)
2. Click "Named Entity Recognition" in sidebar
3. Click "Run Analysis"
4. **Verify**:
   - Preview shows color-coded entities
   - Pie chart shows entity distribution
   - Table shows: entity text + type + confidence
   - Insights show total entities + avg confidence

**Expected Results**:
- ✅ Pink highlight for PER (Person)
- ✅ Blue highlight for ORG (Organization)
- ✅ Green highlight for LOC (Location)
- ✅ Yellow for MISC, etc.
- ✅ Entity distribution chart
- ✅ Table with all entities

---

### Test 3: LangExtract Flow

**Steps**:
1. Upload document (auto-converts)
2. Click "Language Extract" in sidebar
3. Click "Run Analysis"
4. **Verify**:
   - HTML visualization appears
   - Class breakdown shows extraction categories
   - Table shows extractions with classes
   - Insights show total extractions + unique classes

**Expected Results**:
- ✅ Structured extraction visualization
- ✅ Breakdown by class type
- ✅ Table with all extractions
- ✅ Correct counts in insights

---

## 🚨 Error Handling

### Error Scenarios Covered:

#### 1. **Backend Not Running**
```
Error: Failed to convert document
Detail: fetch failed / Connection refused
```
**Solution**: Start backend (`python start_backend.py`)

#### 2. **Invalid File Format**
```
Error: Unsupported file format
Detail: .xyz not supported
```
**Solution**: Upload PDF, DOCX, TXT, etc.

#### 3. **Conversion Failure**
```
Error: Conversion failed
Detail: Error converting document: ...
```
**Solution**: Check backend logs, try different file

#### 4. **Analysis Failure**
```
Error: Processing failed
Detail: Error analyzing sentiment: ...
```
**Solution**: Check backend logs, ensure models loaded

#### 5. **Large File Timeout**
```
Error: Request timeout
```
**Solution**: Try smaller file, increase timeout

---

## 📈 Performance Metrics

### Expected Timings:

| Operation | Expected Time | Depends On |
|-----------|--------------|------------|
| **Document Upload** | < 1 sec | File size |
| **Conversion** | 2-10 sec | File size, format |
| **Sentiment Analysis** | 3-15 sec | Text length |
| **NER Analysis** | 3-12 sec | Text length |
| **LangExtract** | 5-20 sec | Text length, API |

### First-Time vs Subsequent:

**First Time** (Models download):
- Sentiment: +2-5 min (FinBERT download)
- NER: +2-3 min (BERT NER download)
- LangExtract: Normal (uses API)

**Subsequent Times**:
- All analyses use cached models
- Much faster!

---

## 🔍 Debugging Tips

### Check Browser Console:
```javascript
// Open DevTools (F12) → Console

// Look for:
"Conversion error:" // Document conversion failed
"Processing error:" // Analysis failed
"Failed to fetch"   // Backend not running
"CORS error"        // CORS misconfigured
```

### Check Network Tab:
```
F12 → Network tab

// Look for:
POST /convert → Status 200 ✅
POST /analyze → Status 200 ✅
POST /recognize → Status 200 ✅
POST /extract → Status 200 ✅

// If Status 500/404/CORS:
Click request → Response tab → See error details
```

### Check Backend Logs:
```
// In terminal running start_backend.py

// Look for:
INFO: Uvicorn running on ...  ✅
Loading model...               ✅
Model loaded successfully!     ✅

ERROR: ...                     ❌
Traceback: ...                 ❌
```

---

## ✅ Complete Workflow Checklist

Before deployment, verify:

- [ ] Document uploads successfully
- [ ] HTML preview appears after upload
- [ ] Sentiment analysis works end-to-end
- [ ] NER analysis works end-to-end
- [ ] LangExtract works end-to-end
- [ ] Charts render correctly for all types
- [ ] Tables populate correctly for all types
- [ ] Error messages show for failures
- [ ] Loading states display properly
- [ ] "Clear" button resets everything
- [ ] Can switch between analysis types
- [ ] No double conversion happens
- [ ] All 4 backend services respond
- [ ] Frontend connects to all services
- [ ] CORS allows requests
- [ ] No console errors
- [ ] No network errors

---

## 🎓 Summary

**Optimized Workflow**:
1. Upload → Auto-convert → Show preview
2. Select analysis type
3. Click "Run Analysis" → Reuse conversion
4. Display results (preview + chart + table)

**Key Features**:
- ✅ Automatic conversion on upload
- ✅ Immediate HTML preview
- ✅ No duplicate conversions
- ✅ Cached conversion data
- ✅ Smooth state transitions
- ✅ Clear loading indicators
- ✅ Comprehensive error handling
- ✅ Fast subsequent analyses

**This workflow ensures the best user experience with minimal wait times!**
