# Garment sample dataset

Realistic sample data for a knitwear / garment unit (Tirupur-style), covering the full flow:
**yarn → fabric → trims → packing → finished goods.**

> **Note:** this is *synthetic* data modelled on how a garment factory works – item types,
> units, price ranges (INR), suppliers and document numbers are realistic, but supplier and
> customer names are fictional and nothing comes from a real company's books.
> To use your own real figures, replace the CSV files (same columns) and run the seed again.

| File | Rows | Contents |
|---|---|---|
| `warehouses.csv` | 6 | 5 active stores + 1 closed godown (inactive) |
| `items.csv` | 67 | 10 yarn, 20 fabric (+1 discontinued), 18 trims, 10 packing, 8 finished goods |
| `stock_transactions.csv` | 1,612 | Stock in / stock out, 1 Jul 2026 → 28 Sep 2026 |
| `expected_current_stock.csv` | 69 | The balances you should see after loading (used as a self-check) |

## Columns

**items.csv** – `code, name, category, uom, reorder_level, unit_cost, is_active`
**warehouses.csv** – `name, location, is_active`
**stock_transactions.csv** – `transaction_date, transaction_type (IN/OUT), item_code, warehouse_name, quantity, unit_cost, supplier, remarks`
(`unit_cost` and `supplier` are only filled for `IN` rows.)

## What the data lets you test

- Every item has stock in and stock out history; **no stock-out ever exceeds the available stock**.
- **17 stock lines are LOW** (quantity ≤ reorder level), including **2 that are completely out of stock**.
- Three packing items (`PKG001`, `PKG003`, `PKG005`) are held in **two warehouses**, to show per-warehouse balances.
- `FAB099` (discontinued item) and *Old Godown (Closed)* are **inactive** – the app must refuse stock movements against them.
- Units include KG, MTR, PCS, CONE and ROLL; KG/MTR quantities have decimals (e.g. 3452.5).

## Loading it

For local SQLite development, the backend creates its tables and loads the
dataset automatically on first startup:

```bash
cd backend
uvicorn app.main:app --reload
```

To load into a PostgreSQL database, configure `DATABASE_URL`, create the schema
with `alembic upgrade head`, then run `python -m scripts.seed`. The seed command
refuses to load into non-empty inventory tables. To replace existing items,
warehouses and stock transactions, run `python -m scripts.seed --reset`. This
deletes data from those three tables before loading; it does not drop the tables
or other database objects.

For local development on Windows, start the backend and frontend in separate
PowerShell terminals:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

In a second terminal, point the frontend at that API:

```powershell
cd frontend
npm run dev -- --port 5173
```

The script goes through the normal services, then compares the result to
`expected_current_stock.csv` and prints "Check passed" when they match.

## Regenerating

From the project root, `python data/generate_dataset.py` rebuilds all four CSV files. The random
seed is fixed, so it produces the same data every time; change the seed or the item lists at the
top of the file to get a different set.
