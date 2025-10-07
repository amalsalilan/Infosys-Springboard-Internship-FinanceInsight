# FinSight Troubleshooting Guide

## Common Errors and Solutions

### NetworkError when attempting to fetch resource

**Problem**: The frontend cannot connect to the backend services.

**Cause**: Backend services are not running on the required ports.

**Solution**:

1. Start the backend services:
   python start_backend.py

2. Verify services are running - you should see:
   - Document Converter on http://127.0.0.1:8000
   - Sentiment Analysis on http://127.0.0.1:8001
   - NER Service on http://127.0.0.1:8002
   - LangExtract Service on http://127.0.0.1:8003

3. Test services manually by visiting:
   http://localhost:8000/health
   http://localhost:8001/health
   http://localhost:8002/health
   http://localhost:8003/health

4. Start the frontend in a separate terminal:
   npm run dev

## Quick Start

1. Terminal 1 - Start Backend:
   python start_backend.py

2. Terminal 2 - Start Frontend:
   npm run dev

3. Open browser:
   http://localhost:8080

## Service Port Reference

| Service | Port | Health Check |
|---------|------|-------------|
| Document Converter | 8000 | http://localhost:8000/health |
| Sentiment Analysis | 8001 | http://localhost:8001/health |
| NER Service | 8002 | http://localhost:8002/health |
| LangExtract | 8003 | http://localhost:8003/health |
| Frontend | 8080 | http://localhost:8080 |
