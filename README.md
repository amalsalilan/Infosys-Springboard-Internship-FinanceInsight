# FinSight - Financial Document Analysis

## Prerequisites

- Python 3.10+
- Node.js 16+
- Git
- uv (Python package manager)

## Setup

**1. Clone the repository:**
```bash
git clone https://github.com/amalsalilan/Infosys-Springboard-Internship-FinanceInsight.git
cd Infosys-Springboard-Internship-FinanceInsight
```

**2. Install uv (if not already installed):**
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**3. Install Python dependencies:**
```bash
uv sync

# On Windows, also install libmagic for langextract service:
uv pip install python-magic-bin
```

**4. Install Node dependencies:**
```bash
npm install
```

## Running the Application

**1. Start backend services:**
```bash
uv run python scripts/start_backend.py
```

**2. Start frontend (in a new terminal):**
```bash
npm run dev
```


**3. Access the application:**
Open your browser and navigate to `http://localhost:8080`

