# ai-pitch-backend

[![CI](https://github.com/lrddrl/ai-pitch-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/lrddrl/ai-pitch-backend/actions/workflows/ci.yml)

FastAPI service that scores startup pitch decks using GPT-4.1-nano across 10 VC evaluation criteria, with PDF parsing, OCR fallback, macro-risk analysis, and scoring-consistency measurement.

## Features

- **PDF pitch scoring** (`/score`) — Accepts one or more uploaded pitch PDFs (or raw text in JSON body), extracts text via PyMuPDF, falls back to Tesseract OCR when extracted text is too short, and asks GPT-4.1-nano to score on 10 VC criteria with score + color + justification
- **Full investment analysis report** (`/generate_analysis_report`) — Generates a structured VC report (summary, weighted categories, competitive landscape, risks, recommendations, key questions, conclusion) in a single JSON response
- **Macro-risk analysis** (`/macro_risk_analysis`) — Pulls the latest 12 months of USA macro trends from the local `macro_trends` table (loaded from OECD via `pandasdmx`) and produces a written ESG/political/economic risk analysis
- **Scoring consistency** (`/consistency_analysis`) — Computes standard deviation across multiple score runs to flag "low / moderate / very consistent" LLM behavior
- **Batch scoring** (`/batch_score`) — Runs the simple-scoring prompt 30 times on the same input to power the consistency measurement above
- **Score key normalization** — Maps GPT's free-form criterion names to the canonical 10-criterion schema (Leadership, Financials, Market Size, GTM Strategy, Technology/IP, Exit Potential, Competition, Risk, Deal Terms, Traction)

## Tech Stack

- **API**: FastAPI, Uvicorn, python-multipart
- **LLM**: OpenAI Python SDK (`gpt-4.1-nano-2025-04-14`)
- **PDF / OCR**: PyMuPDF (`fitz`), `pdf2image`, `pytesseract`
- **Persistence**: PostgreSQL via `psycopg2` (raw) and SQLAlchemy
- **Validation**: Pydantic v1
- **Data / ETL**: pandas, pandasdmx (OECD loader), openpyxl
- **Async DB**: `databases[asyncpg]`, asyncpg

## Architecture

A single FastAPI app in `main.py` exposes the five scoring endpoints and one health check. The PDF pipeline reads bytes from `UploadFile`, writes to a `temp.pdf` (re-used across files in a batch), opens it with PyMuPDF, and switches to Tesseract OCR if the extracted text is under 100 characters. Prompts are stored inline in `main.py`; OpenAI calls go through the official SDK. PostgreSQL access uses two paths: raw `psycopg2` in `db.py` (for `pitch_scores` persistence) and SQLAlchemy (for the OECD macro loader in `load_oecd.py`).

```
Client (PDF or text)
        │
        ▼
  FastAPI /score  ──►  PyMuPDF text extract
        │                    │
        │            <100 chars?
        │              ┌─────┴─────┐
        │             yes          no
        │              │            │
        │              ▼            ▼
        │       Tesseract OCR   (use text)
        │              │            │
        │              └─────┬──────┘
        │                    ▼
        │          OpenAI GPT-4.1-nano
        │           (10-criterion prompt)
        │                    ▼
        │       normalize keys → JSON
        ▼
   {scores, preview_text}

Other endpoints:
  /generate_analysis_report  → VC report JSON
  /macro_risk_analysis       → OECD macro + LLM
  /consistency_analysis      → std-dev across runs
  /batch_score               → 30x simple score loop
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Tesseract OCR installed at `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows) — adjust the `pytesseract.pytesseract.tesseract_cmd` path in `main.py` for other OSes
- Poppler binaries on disk (used by `pdf2image`)
- An OpenAI API key

### Setup

```bash
git clone https://github.com/lrddrl/ai-pitch-backend.git
cd ai-pitch-backend

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Environment

Create a `.env` file in the project root (see `.env.example` for the template):

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ai_pitch_db
```

Update `main.py`'s `get_engine()` and `db.py`'s `DB_*` defaults to point at your local Postgres, or wire them through env vars.

### Database bootstrap

```bash
# 1. Create the DB
createdb ai_pitch_db

# 2. Initialize the pitch_scores table
python init_and_seed.py

# 3. (Optional) Seed or insert demo data
python insert_fake_data.py
python insert_single_pitch_data.py

# 4. (Optional) Load the latest OECD macro indicators
python load_oecd.py
```

### Run the API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The OpenAPI docs are served at `http://localhost:8000/docs`.

### Try the `/score` endpoint

```bash
curl -X POST http://localhost:8000/score \
  -F "files=@./temp.pdf"
```

You should get back a JSON object with `scores` (per-criterion score + color + justification), `preview_text`, and `preview_text_full`.

## Endpoints

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET    | `/`                          | Health check |
| POST   | `/score`                     | PDF or text → 10-criterion scores |
| POST   | `/generate_analysis_report`  | Scores + project text → full VC report JSON |
| POST   | `/macro_risk_analysis`       | Startup text + OECD macro → macro risk write-up |
| POST   | `/consistency_analysis`      | List of score runs → std-dev / mean / consistency label |
| POST   | `/batch_score`               | Text → array of 30 simple scores (drives consistency) |

## Notes

- The default model is `gpt-4.1-nano-2025-04-14` — swap in `gpt-4o` or `gpt-4-turbo` in `main.py` if you need higher-quality justifications at higher cost.
- The `cfa_factors` list in `main.py` is a legacy display name list; the live scoring rubric is the 10-criterion list in `score_pitch_with_openai` / `score_pitch_simple`.
- `temp.pdf` is reused across files in a single request batch; clear it between calls if you need isolation.
