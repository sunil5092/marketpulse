# 📈 MarketPulse — Real-Time Stock & News Data Pipeline

> End-to-end data engineering project: automated ETL pipeline that fetches live stock prices and financial news, transforms and loads into PostgreSQL, and serves a React dashboard.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org)
[![APScheduler](https://img.shields.io/badge/APScheduler-3.10-orange?style=flat-square)](https://apscheduler.readthedocs.io)

---

## 🎯 What It Does

MarketPulse is a production-style data pipeline that runs continuously:

| Component | Description |
|---|---|
| **ETL Pipeline** | Extract → Transform → Load for stock prices and financial news |
| **Scheduler** | APScheduler runs the pipeline automatically every 30 minutes |
| **Database** | PostgreSQL stores OHLCV prices, news articles, and pipeline audit logs |
| **REST API** | FastAPI serves data to the dashboard and exposes pipeline controls |
| **Dashboard** | React app with live price cards, charts, news feed, and pipeline monitor |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Data Sources                        │
│  Yahoo Finance (free)  │  NewsAPI (free tier)    │
└───────────┬────────────────────────┬────────────┘
            │ fetcher.py             │
            ▼                        ▼
┌─────────────────────────────────────────────────┐
│           ETL Pipeline (pipeline.py)             │
│                                                  │
│  EXTRACT   fetcher.py   → raw DataFrames/dicts  │
│  TRANSFORM transformer.py → clean, enrich        │
│  LOAD      loader.py    → PostgreSQL upsert      │
│                                                  │
│  Triggered by: APScheduler (every 30 min)        │
│             or: POST /api/pipeline/run           │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              PostgreSQL Database                  │
│  stock_prices   │  news_articles  │  pipeline_runs│
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│            FastAPI Backend                        │
│  /api/dashboard  /api/stocks  /api/news          │
│  /api/pipeline   /api/health                     │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│            React Frontend                         │
│  Dashboard │ Stocks (chart) │ News │ Pipeline     │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
marketpulse/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, scheduler startup, CORS
│   │   ├── config.py                # All config from .env
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── api/
│   │   │   ├── health.py            # GET /api/health
│   │   │   ├── stocks.py            # GET /api/stocks/*
│   │   │   ├── news.py              # GET /api/news/*
│   │   │   ├── pipeline.py          # POST /api/pipeline/run + GET runs
│   │   │   └── dashboard.py         # GET /api/dashboard (aggregated BFF)
│   │   ├── models/
│   │   │   ├── orm.py               # SQLAlchemy table definitions
│   │   │   └── schemas.py           # Pydantic API schemas
│   │   ├── services/
│   │   │   ├── fetcher.py           # EXTRACT: Yahoo Finance + NewsAPI
│   │   │   ├── transformer.py       # TRANSFORM: clean, enrich, classify
│   │   │   ├── loader.py            # LOAD: PostgreSQL upsert
│   │   │   └── pipeline.py          # Orchestrator: wires ETL together
│   │   └── scheduler/
│   │       └── jobs.py              # APScheduler background job
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    └── src/
        ├── App.jsx                  # Root + page routing
        ├── api.js                   # All API calls
        ├── constants.js
        ├── components/
        │   └── Navbar.jsx
        └── pages/
            ├── Dashboard.jsx        # Overview: stock cards + news
            ├── Stocks.jsx           # Price chart + OHLCV table
            ├── News.jsx             # News feed with filters
            └── Pipeline.jsx         # ETL controls + audit log
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL running locally (or Docker)

### 1. Set up PostgreSQL

```bash
# Option A — Docker (easiest)
docker run --name marketpulse-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=marketpulse \
  -p 5432:5432 -d postgres:16

# Option B — Local PostgreSQL
createdb marketpulse
```

### 2. Backend

```bash
cd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env — set DATABASE_URL and optionally NEWS_API_KEY

uvicorn app.main:app --reload --port 8000
```

On startup, the app:
- Creates all database tables automatically
- Starts the APScheduler background job
- API is live at `http://localhost:8000`
- Swagger docs at `http://localhost:8000/docs`

### 3. Trigger the first pipeline run

```bash
# Via curl
curl -X POST http://localhost:8000/api/pipeline/run

# Or via the Dashboard UI — click "▶ Run Pipeline"
```

### 4. Frontend

```bash
cd frontend
npm install
npm start
```

App opens at `http://localhost:3000`

### 5. Tests

```bash
cd backend
pytest tests/ -v
```

---

## 📡 Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard` | Full dashboard data in one call |
| GET | `/api/stocks/summary` | Price summary cards for all tickers |
| GET | `/api/stocks/{ticker}/history` | OHLCV history for one ticker |
| GET | `/api/news` | News feed (filter by ticker, sentiment) |
| GET | `/api/news/sentiment-summary` | Sentiment breakdown counts |
| POST | `/api/pipeline/run` | Trigger full ETL pipeline |
| GET | `/api/pipeline/runs` | Pipeline audit log |
| GET | `/api/health` | Health + DB connectivity check |

---

## 🗄️ Database Schema

```sql
-- OHLCV price history
stock_prices (id, ticker, date, open, high, low, close, volume, pct_change, created_at)

-- Financial news with sentiment
news_articles (id, ticker, title, description, url, source, published_at, sentiment, created_at)

-- ETL audit log
pipeline_runs (id, run_type, status, tickers_fetched, rows_inserted, rows_skipped,
               error_message, started_at, finished_at, duration_secs)
```

---

## 🔑 Getting a Free NewsAPI Key

1. Go to [newsapi.org](https://newsapi.org)
2. Click "Get API Key" — free tier gives 100 requests/day
3. Add it to your `.env`: `NEWS_API_KEY=your_key_here`

> Without a key the pipeline still works using built-in mock news data so you can demo the full system.

---

## 🧠 What This Project Demonstrates

| Skill | Where |
|---|---|
| **ETL pipeline design** | `services/fetcher.py` → `transformer.py` → `loader.py` |
| **Data cleaning** | Null handling, deduplication, type conversion, derived metrics in `transformer.py` |
| **SQL / ORM** | SQLAlchemy models, queries, upsert strategy in `models/orm.py` + `loader.py` |
| **Scheduling** | APScheduler background jobs in `scheduler/jobs.py` |
| **REST API design** | FastAPI with Pydantic validation, dependency injection |
| **Data modeling** | 3 normalized tables with indexes and constraints |
| **Audit logging** | Every pipeline run logged with status, counts, and duration |
| **Full stack** | React dashboard consuming the API with charts (Recharts) |

---

## 👨‍💻 Author

**Sunil KM** — MS Applied CS @ Southeast Missouri State University

[![LinkedIn](https://img.shields.io/badge/LinkedIn-msunil2002-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/msunil2002/)
[![GitHub](https://img.shields.io/badge/GitHub-sunil5092-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/sunil5092)

*F1 OPT — Authorized to work in the US*
