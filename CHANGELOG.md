# Changelog

All notable changes to the FinSight project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-04

### Added

#### LangExtract Module
- **Custom Configuration Dialog** (`LangExtractConfigDialog.tsx`)
  - Interactive form builder for extraction configuration
  - JSON input mode for advanced users
  - Dual input modes: Form Builder and JSON Input
  - Real-time JSON validation with error messages
  - Reference guide accordion with example JSON structure
  - Financial domain placeholders and examples

- **Navigation Controls**
  - Play/Previous/Next buttons for stepping through extractions
  - Visual highlighting of current extraction in HTML viewer
  - Auto-scroll to active extraction (smooth scroll behavior)
  - Position counter display (e.g., "3 / 10")
  - `data-extraction-index` attributes in HTML for navigation

- **Fallback Examples System**
  - Default contract-based examples when user provides none
  - Termination clauses, obligations, governing law examples
  - Automatic injection when examples field is empty
  - User examples take precedence when provided

- **Auto-scaling Layout**
  - Bottom extraction panel grows with content (max-height: 70vh)
  - Overflow-y: auto for long content scrolling
  - Fixed top preview (400px) for stable layout
  - Module-specific layout: LangExtract uses auto-scale, others use fixed heights

#### Named Entity Recognition (NER)
- **Inline Entity Labels**
  - Entity type displayed directly in text as `[TYPE]` superscript
  - Example: `Beta Telecom Services [ORG]`, `$2,500,000 [MONEY]`
  - Removed standalone "Entity Types" legend from UI
  - Cleaner HTML output with just content (no legend section)

- **Enhanced Styling**
  - Increased line-height (1.8) for better readability
  - Inline-block display for proper label positioning
  - Font-size: 0.65em for type labels
  - Bold and semi-transparent labels for subtle emphasis

#### General UI/UX
- **Active State Indicators**
  - Left border highlight for selected analysis mode in sidebar
  - Bold text and shadow for active module
  - Smooth transitions (duration-200)

- **Error Handling**
  - Specific error detection for network/fetch errors
  - Backend service unavailability messages
  - Actionable error messages with exact commands
  - Created TROUBLESHOOTING.md guide

- **Document State Persistence**
  - Upload state preserved when switching between analysis modes
  - Conversion data retained across mode changes
  - Fixed "Process Document" button re-enable logic

### Changed

#### Layout & Responsiveness
- Changed preview area from `h-[60%]` to fixed `h-[400px]`
- Bottom panel: conditional `max-h-[70vh]` for LangExtract, `h-[40%]` for others
- Improved overflow handling with internal scrolling
- Consistent layout regardless of document length

#### Navigation
- Navigation buttons now **only appear in LangExtract module**
- Removed navigation from Sentiment Analysis and NER modules
- Active extraction highlighted in table with left border (`border-l-4 border-l-primary`)
- Table row `data-table-row` attribute for scroll targeting

#### Backend Services
- **LangExtract Service**
  - Added BeautifulSoup post-processing for HTML visualization
  - Inject `data-extraction-index` attributes to highlighted elements
  - Support for marks, spans with background, and highlight classes

- **Unicode Handling**
  - Force UTF-8 encoding on Windows stdout/stderr
  - Unicode normalization (NFC) for all input text
  - Explicit UTF-8 encoding in file I/O operations
  - Fallback JSONL saving with error handling
  - Created `test_unicode_handling.py` test suite

- **NER Service**
  - Updated highlight function to add inline labels
  - Removed legend HTML from output
  - Simplified HTML structure

### Fixed

- **Bundle Size Optimization**
  - Fixed dynamic import warnings
  - Added manual chunks (react-vendor, ui-vendor, charts)
  - Reduced initial bundle size with code splitting
  - All chunks under 360KB

- **Mode Switching Bug**
  - Fixed app crashes when switching between analysis modes
  - Added type guards (isSentimentResponse, isNERResponse, isLangExtractResponse)
  - Try-catch blocks around rendering logic
  - Document reference preserved across switches

- **Process Document Button**
  - Fixed button disable/enable flow
  - Consistent styling with Upload button
  - Loading spinner with proper states
  - Icon updates (Play for process, Loader2 for loading)

- **Unicode/Encoding Errors**
  - Fixed `charmap codec can't encode character` errors
  - Handle special characters (✓, ✗, emojis, non-Latin scripts)
  - Safe for international text and financial symbols

- **Layout Overflow**
  - Fixed long documents pushing extraction table below viewport
  - Stable height layout prevents preview squeezing
  - Internal scrolling for both preview and table

### Technical Details

#### Files Modified
- `src/pages/Index.tsx` - Main application logic with navigation handlers
- `src/components/ExtractionsTable.tsx` - Navigation controls and active highlighting
- `src/components/LangExtractConfigDialog.tsx` - Created custom config dialog
- `src/components/Sidebar.tsx` - Active state visual indicators
- `src/components/InsightsPanel.tsx` - Type guards and error handling
- `langextract_service.py` - HTML post-processing and data attributes
- `ner_service.py` - Inline labels and legend removal
- `sentiment_service.py` - Unicode handling (reverted navigation attributes)
- `vite.config.ts` - Manual chunks for bundle optimization

#### New Files
- `src/components/LangExtractConfigDialog.tsx` - LangExtract configuration UI
- `test_unicode_handling.py` - Unicode character test suite
- `TROUBLESHOOTING.md` - User troubleshooting guide
- `CHANGELOG.md` - This file

### Performance

- **Code Splitting**: React vendor (141KB), UI vendor (109KB), Charts (359KB), Index (155KB)
- **Lazy Loading**: Dynamic imports for heavy components (removed for stability)
- **Cache Strategy**: Browser caching for vendor bundles

---

## [1.0.0] - 2025-10-03

### Added

#### Core Features
- **Document Converter Service** (Port 8000)
  - Support for PDF, DOCX, XLSX, PPTX, HTML, CSV, Markdown
  - Text, Markdown, and HTML output formats
  - Docling-based conversion pipeline

- **Sentiment Analysis Service** (Port 8001)
  - FinBERT model for financial sentiment
  - Sentence-level classification (Positive, Negative, Neutral)
  - Confidence scores and HTML highlighting
  - Color-coded visualization

- **NER Service** (Port 8002)
  - Financial entity recognition
  - Entity types: ORG, PER, LOC, MONEY, DATE, PERCENT, MISC
  - Color-coded entity highlighting
  - HTML visualization with legend

- **LangExtract Service** (Port 8003)
  - Google Gemini-powered extraction
  - Custom prompt and examples support
  - Structured data extraction
  - HTML visualization

#### Frontend
- React 18 + TypeScript setup
- Tailwind CSS styling
- shadcn/ui component library
- Recharts for data visualization
- Document upload with drag & drop
- Three analysis modes (Sentiment, NER, LangExtract)
- Real-time preview and results display

#### Infrastructure
- FastAPI backend services
- CORS configuration for local development
- Vite proxy for API routing
- Unified backend startup script (`start_backend.py`)
- Health check endpoints for all services

### Technical Stack
- **Frontend**: React 18.3, TypeScript 5.5, Vite, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **AI/ML**: FinBERT, Transformers, LangExtract, Google Gemini
- **Tools**: BeautifulSoup4, Docling, httpx

---

## Version History Summary

- **v1.1.0** (2025-10-04) - Major UI/UX enhancements, navigation, inline labels, auto-scaling
- **v1.0.0** (2025-10-03) - Initial release with core analysis features

---

## Migration Guide

### Upgrading from 1.0.0 to 1.1.0

#### Breaking Changes
- None. All changes are backward compatible.

#### New Dependencies
- BeautifulSoup4 (already in requirements.txt)
- No new npm packages

#### Configuration Changes
- No configuration changes required
- Existing backend services work without modification

#### UI Changes
- NER now shows inline labels instead of legend (no action needed)
- LangExtract has new navigation controls (optional feature)
- Layout is more responsive (automatic)

#### Steps to Upgrade
```bash
# 1. Pull latest code
git pull origin main

# 2. Reinstall dependencies (optional, recommended)
npm install
pip install -r requirements.txt

# 3. Rebuild frontend
npm run build

# 4. Restart backend services
python start_backend.py
```

---

## Upcoming Features (Roadmap)

### Planned for v1.2.0
- [ ] Multi-document batch processing
- [ ] Export results to PDF/Excel
- [ ] User authentication and session management
- [ ] Document history and saved analyses
- [ ] Advanced filtering and search in results
- [ ] Custom theme support (dark mode)
- [ ] API rate limiting and caching
- [ ] Improved error recovery

### Under Consideration
- [ ] Additional LLM providers (OpenAI, Anthropic)
- [ ] Real-time collaborative analysis
- [ ] Document comparison feature
- [ ] Custom model fine-tuning
- [ ] REST API for third-party integrations
- [ ] Mobile-responsive design

---

## Support & Feedback

For bug reports and feature requests:
- Create an issue on GitHub
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review documentation at [README.md](README.md)

---

**Last Updated**: October 4, 2025
