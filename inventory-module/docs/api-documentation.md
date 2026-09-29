# API documentation

Base URL: `http://localhost:8000` — interactive docs at `/docs`.

Errors are returned as `{"detail": "message"}` with these status codes:
`404` not found · `409` duplicate · `422` validation error or business-rule violation (e.g. insufficient stock).

## Items

| Method | Path          | Description                                              |
|--------|---------------|----------------------------------------------------------|
| GET    | `/items`      | List items. Query: `q`, `active_only`, `skip`, `limit`   |
| POST   | `/items`      | Create an item                                           |
| GET    | `/items/{id}` | Get one item                                             |

```json
POST /items
{ "code": "FAB001", "name": "Cotton Fabric", "category": "Fabric",
  "uom": "KG", "reorder_level": 100, "unit_cost": 250 }
```

## Warehouses

| Method | Path               | Description       |
|--------|--------------------|-------------------|
| GET    | `/warehouses`      | List (`active_only`) |
| POST   | `/warehouses`      | Create            |
| GET    | `/warehouses/{id}` | Get one           |

```json
POST /warehouses
{ "name": "Fabric Store", "location": "Block A" }
```

## Stock

| Method | Path                    | Description                                                     |
|--------|-------------------------|-----------------------------------------------------------------|
| POST   | `/stock-in`             | Receive stock                                                   |
| POST   | `/stock-out`            | Issue stock (rejected with 422 if quantity > available)         |
| GET    | `/stock/current`        | Current stock. Query: `warehouse_id`, `item_id`, `q`, `low_only` |
| GET    | `/stock/current/export` | Same filters, returned as a CSV download                        |
| GET    | `/stock/available`      | Available quantity. Query: `item_id`, `warehouse_id`            |
| GET    | `/stock/transactions`   | History. Query: `item_id`, `warehouse_id`, `transaction_type`, `limit` |
| GET    | `/stock/summary`        | Totals for the dashboard                                        |

```json
POST /stock-in
{ "item_id": 1, "warehouse_id": 1, "quantity": 500, "unit_cost": 240,
  "supplier": "ABC Textiles", "transaction_date": "2026-01-15", "remarks": "PO-1042" }

POST /stock-out
{ "item_id": 1, "warehouse_id": 1, "quantity": 70, "transaction_date": "2026-01-16" }
```

`GET /stock/current` row:

```json
{ "item_id": 1, "item_code": "FAB001", "item_name": "Cotton Fabric", "category": "Fabric",
  "warehouse_id": 1, "warehouse_name": "Fabric Store", "uom": "KG",
  "quantity": 400, "reorder_level": 100, "status": "NORMAL" }
```

## Health

`GET /health` → `{"status": "ok"}`
