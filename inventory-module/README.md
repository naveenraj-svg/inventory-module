# Inventory Module

A small inventory system: **item master, warehouses, stock in, stock out, current stock, low-stock alerts and CSV export.**

| Layer    | Tech                                              |
|----------|---------------------------------------------------|
| Backend  | FastAPI, SQLAlchemy 2, Alembic, SQLite / PostgreSQL |
| Frontend | React 18, Vite, React Router, plain CSS           |
| Tests    | pytest (in-memory SQLite, no PostgreSQL needed)   |

## Features

- Item master (code, name, category, UOM, reorder level, unit cost)
- Warehouse master
- Stock in (supplier, unit cost, date, remarks)
- Stock out with **negative-stock prevention** (checked on the backend, previewed on the frontend)
- Current stock = total in − total out, per item and warehouse
- Low-stock flag (quantity ≤ reorder level) and "low stock only" filter
- CSV export of current stock (respects the active filters)
- Dashboard with totals, low-stock lines and recent transactions

## Getting started

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # Windows: Copy-Item .env.example .env
uvicorn app.main:app --reload
```

By default, the backend creates `backend/inventory.db` and loads the sample
dataset from `data/` automatically the first time it starts. No separate
database server, migration, or seed command is needed for local SQLite use.

To use PostgreSQL instead, set `DATABASE_URL` in `backend/.env`, create the
database, and run `alembic upgrade head` before starting the backend. PostgreSQL
does not load the sample dataset automatically; run `python -m scripts.seed`
from `backend` if its inventory tables are empty.

API: <http://localhost:8000> · Interactive docs: <http://localhost:8000/docs>

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: <http://localhost:5173>
(If the API is not on `http://localhost:8000`, set `VITE_API_URL` in `frontend/.env`.)

### 3. Tests

```bash
cd backend
pytest
```

## Project layout

```
inventory-module/
├── backend/    FastAPI app (models, schemas, routers, services, migrations, tests)
├── frontend/   React + Vite app
├── docs/       architecture, database design, API reference
└── screenshots/
```

See `docs/` for details.

## Suggested Git workflow

One feature branch and pull request per day of work:

```
main
 ├── intern/<yourname>/item-master          → PR #1  (items)
 ├── intern/<yourname>/warehouse-stock-in   → PR #2  (warehouses + stock in)
 └── intern/<yourname>/stock-out-csv        → PR #3  (stock out, current stock, CSV)
```

## Design notes

- **Business rules live in `services/`**, not in the routers.
- **Stock is derived, not stored.** There is no "quantity" column to drift out of sync; current stock is always computed from `stock_transactions`.
- **Stock-out is validated on the server.** The frontend check is only for quick feedback. On PostgreSQL the item row is locked during a stock-out, so two simultaneous requests cannot both spend the same stock.
- Item codes are stored upper-case and are unique; warehouse names are unique (case-insensitive).
- CSV export neutralises cells that start with `= + - @` to avoid spreadsheet formula injection.
