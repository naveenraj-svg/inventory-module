# Architecture

```
React (Vite)  ──HTTP/JSON──▶  FastAPI  ──SQLAlchemy──▶  PostgreSQL
```

## Backend layers

| Layer       | Folder            | Responsibility                                           |
|-------------|-------------------|----------------------------------------------------------|
| Routers     | `app/routers`     | HTTP endpoints; parse input, call a service, return JSON |
| Schemas     | `app/schemas`     | Pydantic request/response models and input validation    |
| Services    | `app/services`    | Business rules (duplicates, stock calculation, stock-out) |
| Models      | `app/models`      | SQLAlchemy tables                                        |
| Database    | `app/database`    | Engine, session dependency, declarative base             |
| Core        | `app/core`        | Settings and shared exception types                      |
| Utils       | `app/utils`       | CSV generation                                           |

Errors raised by services (`NotFoundError`, `ConflictError`, `InsufficientStockError`) are converted to JSON responses by a single handler in `app/core/exceptions.py`.

## Frontend layers

| Folder          | Responsibility                                       |
|-----------------|------------------------------------------------------|
| `pages/`        | One component per route                              |
| `forms/`        | Controlled forms with client-side validation         |
| `components/`   | Reusable UI (Table, Modal, Button, Alert, Field…)    |
| `services/api.js` | The only place that calls `fetch`                  |
| `hooks/useApi.js` | Loading / error / reload handling for GET calls    |
| `utils/`        | Validation, number/date formatting, CSV download     |

## Request flow: stock out

```
StockOutForm ─▶ POST /stock-out ─▶ stock_service.stock_out()
                                     1. item + warehouse exist and are active
                                     2. lock the item row
                                     3. available = SUM(in) − SUM(out)
                                     4. quantity > available ? 422 : insert OUT row
```
