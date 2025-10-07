# 👁️ Visual Flow Guide - What You Should See

## 📺 Screen-by-Screen Guide

### Screen 1: Initial State (No Document)

```
┌─────────────────────────────────────────────────────┐
│ Document Analysis                                   │
├──────────────┬──────────────────────┬───────────────┤
│ Sidebar      │   Preview Area       │  Insights     │
│              │                      │               │
│ ✓ Sentiment  │       📄             │  📊 Chart     │
│   NER        │   [File Icon]        │   (Empty)     │
│   LangExtract│                      │               │
│              │   Upload document    │  Insights     │
│              │   to begin analysis  │   (Empty)     │
│              │                      │               │
│              │  [Upload] [Clear]    │               │
│              │                      │               │
│              │  Process Document    │               │
│              │    (disabled)        │               │
└──────────────┴──────────────────────┴───────────────┘
                     Extractions
       ┌───────────────────────────────────────┐
       │ No extractions yet - upload document  │
       └───────────────────────────────────────┘
```

**What to check**:
- [ ] Sidebar shows 3 options
- [ ] Preview area shows file icon
- [ ] "Process Document" button is disabled (grayed out)
- [ ] No errors in browser console (F12)

---

### Screen 2: After Upload (Converting...)

```
┌─────────────────────────────────────────────────────┐
│ Document Analysis                                   │
├──────────────┬──────────────────────┬───────────────┤
│ Sidebar      │   Preview Area       │  Insights     │
│              │                      │               │
│ ✓ Sentiment  │      📄 PDF          │  📊 Chart     │
│   NER        │  your_document.pdf   │   (Empty)     │
│   LangExtract│                      │               │
│              │                      │  Insights     │
│              │    Loading...        │   (Empty)     │
│              │                      │               │
│              │  [Upload] [Clear]    │               │
│              │                      │               │
│              │   Converting...      │               │
│              │    (disabled)        │               │
└──────────────┴──────────────────────┴───────────────┘
```

**What's happening**:
- Backend is converting your document
- Request sent to http://localhost:8000/convert
- Should take 2-10 seconds
- Watch backend terminal for progress

---

### Screen 3: After Conversion (Preview Ready!)

```
┌─────────────────────────────────────────────────────┐
│ Document Analysis                        Toast! ✅  │
├──────────────┬──────────────────────┬──"Document    │
│ Sidebar      │   HTML PREVIEW       │  converted"   │
│              │   ┌────────────────┐ │               │
│ ✓ Sentiment  │   │ Financial      │ │  📊 Chart     │
│   NER        │   │ Report Q4      │ │   (Empty)     │
│   LangExtract│   │                │ │               │
│              │   │ Apple Inc.     │ │  Insights     │
│              │   │ reported...    │ │   (Empty)     │
│              │   │                │ │               │
│              │   │ Revenue: $XX   │ │               │
│              │   └────────────────┘ │               │
│              │  [Upload] [Clear]    │               │
│              │                      │               │
│              │   Run Analysis       │               │
│              │    (enabled!)        │               │
└──────────────┴──────────────────────┴───────────────┘
```

**✅ SUCCESS! What you should see**:
- [x] **HTML preview visible** in center area
- [x] Can scroll through document content
- [x] Toast notification appears (top right)
- [x] Button changes to "Run Analysis"
- [x] Button is now ENABLED (clickable)
- [x] `output/` folder contains 3 files:
  - `your_document.txt`
  - `your_document.md`
  - `your_document.html`

**Backend saved**:
```
output/
├── your_document.txt   ← Plain text for analysis
├── your_document.md    ← Markdown version
└── your_document.html  ← What you see in preview
```

---

### Screen 4: After Clicking "Run Analysis" (Analyzing...)

```
┌─────────────────────────────────────────────────────┐
│ Document Analysis                                   │
├──────────────┬──────────────────────┬───────────────┤
│ Sidebar      │   HTML PREVIEW       │  Insights     │
│              │   ┌────────────────┐ │               │
│ ✓ Sentiment  │   │ Financial      │ │  📊 Chart     │
│   NER        │   │ Report Q4      │ │   Loading...  │
│   LangExtract│   │                │ │               │
│              │   │ Apple Inc.     │ │  Insights     │
│              │   │ reported...    │ │   Loading...  │
│              │   │                │ │               │
│              │   │ Revenue: $XX   │ │               │
│              │   └────────────────┘ │               │
│              │  [Upload] [Clear]    │               │
│              │                      │               │
│              │    Analyzing...      │               │
│              │    (disabled)        │               │
└──────────────┴──────────────────────┴───────────────┘
```

**What's happening**:
- Backend is analyzing document sentiment/NER/extraction
- Takes 5-20 seconds depending on analysis type
- Watch backend terminal for progress

---

### Screen 5: Results! (Complete)

```
┌─────────────────────────────────────────────────────┐
│ Document Analysis                                   │
├──────────────┬──────────────────────┬───────────────┤
│ Sidebar      │  HIGHLIGHTED HTML    │  📊 PIE CHART │
│              │   ┌────────────────┐ │   ┌─────────┐ │
│ ✓ Sentiment  │   │ Financial      │ │   │ •55%    │ │
│   NER        │   │ Report Q4      │ │   │Positive │ │
│   LangExtract│   │                │ │   │ •30%    │ │
│              │   │ Apple Inc.     │ │   │Negative │ │
│              │   │ reported... ✅ │ │   │ •15%    │ │
│              │   │                │ │   │Neutral  │ │
│              │   │ Revenue: $XX ❌│ │   └─────────┘ │
│              │   └────────────────┘ │               │
│              │  [Upload] [Clear]    │  Insights     │
│              │                      │  📈 Stats     │
│              │   Run Analysis       │               │
│              │    (enabled)         │               │
└──────────────┴──────────────────────┴───────────────┘
                     Extractions
       ┌───────────────────────────────────────┐
       │ Sentence              │ Class │ Score │
       │ "This is great news!" │ Pos.  │ 95%   │
       │ "Concerns remain..."  │ Neg.  │ 87%   │
       │ "The company said..." │ Neut. │ 72%   │
       └───────────────────────────────────────┘
```

**✅ COMPLETE! What you should see**:
- [x] Preview shows highlighted text (colors!)
- [x] Chart shows data distribution
- [x] Table shows detailed results
- [x] Insights panel shows statistics
- [x] Can click "Run Analysis" again
- [x] Can switch analysis types and re-run

---

## 🎨 Color Guide

### Sentiment Analysis Colors:
- 🟢 **Green** = Positive sentiment
- 🔴 **Red** = Negative sentiment
- ⚪ **Gray** = Neutral sentiment

### NER Colors:
- 🔵 **Blue** = Organization (ORG)
- 💗 **Pink** = Person (PER)
- 🟢 **Green** = Location (LOC)
- 🟡 **Yellow** = Money, Date, etc.

---

## 🔄 What Happens Behind the Scenes

### Upload & Conversion Flow:

```
User clicks Upload
        ↓
Select file.pdf
        ↓
Frontend: handleFileUpload()
        ↓
POST http://localhost:8000/convert
        ↓
Backend: document_converter.py
        ↓
Docling converts to text/markdown/HTML
        ↓
Save to output/ folder
        ↓
Return JSON: { text, markdown, html }
        ↓
Frontend: setHtmlPreview(html)
        ↓
Display HTML in iframe
        ↓
✅ User sees preview!
```

### Analysis Flow:

```
User clicks "Run Analysis"
        ↓
Frontend: handleProcess()
        ↓
Check if converted? YES (cached!)
        ↓
Send text to analysis service
  - Sentiment: http://localhost:8001/analyze
  - NER: http://localhost:8002/recognize
  - LangExtract: http://localhost:8003/extract
        ↓
Backend processes with AI model
        ↓
Return results + highlighted HTML
        ↓
Frontend: setAnalysisResults()
        ↓
Update preview, chart, table
        ↓
✅ User sees results!
```

---

## 📱 Browser DevTools Verification

### Open DevTools (Press F12)

#### Console Tab - Should show:
```
✅ No errors
✅ No warnings (or only benign ones)
```

#### Network Tab - After upload should show:
```
Name               Status   Type
convert            200      fetch
✅ Click it → Preview tab → Should see HTML content
✅ Click it → Response tab → Should see JSON with html field
```

#### Elements Tab - Should show:
```
<iframe srcDoc="<!DOCTYPE html>...">
✅ This is your preview iframe
✅ Right-click → Inspect to see HTML structure
```

---

## ✅ Quick Verification Checklist

After uploading a document, verify:

- [ ] Toast shows "Document converted"
- [ ] HTML preview appears in center
- [ ] Can see document text/content
- [ ] Button changes to "Run Analysis"
- [ ] Button is enabled (not grayed out)
- [ ] No red errors in browser console
- [ ] Network tab shows 200 status for /convert
- [ ] `output/` folder has 3 new files

If ALL checked ✅ → **Everything is working!**

If ANY unchecked ❌ → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🎯 What This Means

**You now have**:
1. ✅ Document upload working
2. ✅ Automatic conversion working
3. ✅ HTML preview displaying
4. ✅ Text saved for analysis
5. ✅ Foundation for all analysis modules

**Next step**: Test the analysis modules!

---

## 🚀 Ready to Test?

Follow [START_HERE.md](START_HERE.md) for step-by-step instructions!
