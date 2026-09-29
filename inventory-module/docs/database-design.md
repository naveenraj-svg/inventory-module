# Database design

## items
| Column         | Type            | Notes                     |
|----------------|-----------------|---------------------------|
| id             | integer PK      |                           |
| code           | varchar(50)     | unique, stored upper-case |
| name           | varchar(200)    |                           |
| category       | varchar(100)    | nullable                  |
| uom            | varchar(20)     | e.g. KG, PCS, MTR         |
| reorder_level  | numeric(14,3)   | default 0                 |
| unit_cost      | numeric(14,2)   | default 0                 |
| is_active      | boolean         | default true              |
| created_at     | timestamptz     | default now()             |

## warehouses
| Column     | Type         | Notes  |
|------------|--------------|--------|
| id         | integer PK   |        |
| name       | varchar(150) | unique |
| location   | varchar(255) | nullable |
| is_active  | boolean      | default true |
| created_at | timestamptz  | default now() |

## stock_transactions
| Column           | Type          | Notes                                  |
|------------------|---------------|----------------------------------------|
| id               | integer PK    |                                        |
| item_id          | FK → items    | indexed                                |
| warehouse_id     | FK → warehouses | indexed                              |
| transaction_type | varchar(3)    | `IN` or `OUT` (check constraint)       |
| quantity         | numeric(14,3) | must be > 0 (check constraint)         |
| unit_cost        | numeric(14,2) | nullable; used for stock in            |
| supplier         | varchar(200)  | nullable; used for stock in            |
| transaction_date | date          |                                        |
| remarks          | text          | nullable                               |
| created_at       | timestamptz   | default now()                          |

## Relationships

```
items 1 ───< stock_transactions >─── 1 warehouses
```

## Current stock

There is no stored balance. It is computed:

```sql
SELECT item_id, warehouse_id,
       SUM(CASE WHEN transaction_type = 'IN' THEN quantity ELSE -quantity END) AS quantity
FROM stock_transactions
GROUP BY item_id, warehouse_id;
```

A row is **LOW** when `quantity <= items.reorder_level`.

## Migrations

```
0001_create_items → 0002_create_warehouses → 0003_create_stock_transactions
```
