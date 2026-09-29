import argparse
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database.base import Base
from app.database.connection import SessionLocal
from app.models.item import Item
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.schemas.item import ItemCreate
from app.schemas.stock import StockInCreate, StockOutCreate
from app.schemas.warehouse import WarehouseCreate
from app.services import item_service, stock_service, warehouse_service

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def _read_csv(filename: str) -> list[dict[str, str]]:
    with (DATA_DIR / filename).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _as_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"Expected true or false, got {value!r}.")
    return normalized == "true"


def _table_count(db: Session, model: type[Base]) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def _validate_dataset(
    items: list[dict[str, str]],
    warehouses: list[dict[str, str]],
    transactions: list[dict[str, str]],
) -> None:
    item_by_code = {row["code"]: row for row in items}
    warehouse_by_name = {row["name"]: row for row in warehouses}
    if len(item_by_code) != len(items):
        raise ValueError("Dataset contains duplicate item codes.")
    if len(warehouse_by_name) != len(warehouses):
        raise ValueError("Dataset contains duplicate warehouse names.")

    balances: dict[tuple[str, str], Decimal] = {}
    for row in transactions:
        item_code = row["item_code"]
        warehouse_name = row["warehouse_name"]
        item = item_by_code.get(item_code)
        warehouse = warehouse_by_name.get(warehouse_name)
        if item is None or warehouse is None:
            raise ValueError(
                f"Transaction references unknown item or warehouse: "
                f"{item_code!r}, {warehouse_name!r}."
            )
        if not _as_bool(item["is_active"]) or not _as_bool(warehouse["is_active"]):
            raise ValueError(
                f"Transaction references inactive item or warehouse: "
                f"{item_code!r}, {warehouse_name!r}."
            )

        quantity = Decimal(row["quantity"])
        if quantity <= 0:
            raise ValueError("Transaction quantities must be positive.")
        key = (item_code, warehouse_name)
        balance = balances.get(key, Decimal("0"))
        transaction_type = row["transaction_type"].strip().upper()
        if transaction_type == "IN":
            balance += quantity
        elif transaction_type == "OUT":
            balance -= quantity
            if balance < 0:
                raise ValueError(
                    f"Dataset stock-out exceeds available stock for {key!r}."
                )
        else:
            raise ValueError(f"Invalid transaction type: {transaction_type!r}.")
        balances[key] = balance


def _clear_inventory(db: Session) -> None:
    db.execute(delete(StockTransaction))
    db.execute(delete(Item))
    db.execute(delete(Warehouse))
    db.commit()


def _verify_balances(db: Session, expected_rows: list[dict[str, str]]) -> None:
    actual_rows = {
        (row["item_code"], row["warehouse_name"]): row
        for row in stock_service.get_current_stock(db)
    }
    mismatches = []
    for expected in expected_rows:
        key = (expected["item_code"], expected["warehouse_name"])
        actual = actual_rows.get(key)
        if actual is None:
            mismatches.append(f"{key}: missing from current stock")
            continue
        expected_quantity = Decimal(expected["quantity"])
        if Decimal(str(actual["quantity"])) != expected_quantity:
            mismatches.append(
                f"{key}: expected {expected_quantity}, got {actual['quantity']}"
            )
        if actual["status"] != expected["status"]:
            mismatches.append(
                f"{key}: expected status {expected['status']}, got {actual['status']}"
            )
    if mismatches:
        details = "\n".join(mismatches[:10])
        raise ValueError(f"Dataset balance check failed:\n{details}")


def seed_dataset(db: Session, reset: bool = False) -> dict[str, int]:
    items = _read_csv("items.csv")
    warehouses = _read_csv("warehouses.csv")
    transactions = _read_csv("stock_transactions.csv")
    expected_rows = _read_csv("expected_current_stock.csv")
    _validate_dataset(items, warehouses, transactions)

    existing_counts = {
        "items": _table_count(db, Item),
        "warehouses": _table_count(db, Warehouse),
        "transactions": _table_count(db, StockTransaction),
    }
    if any(existing_counts.values()):
        if not reset:
            raise RuntimeError(
                "Inventory tables are not empty. Use --reset to replace their data. "
                f"Current counts: {existing_counts}."
            )
        _clear_inventory(db)

    item_ids = {}
    for row in items:
        item = item_service.create_item(
            db,
            ItemCreate(
                code=row["code"],
                name=row["name"],
                category=row["category"] or None,
                uom=row["uom"],
                reorder_level=Decimal(row["reorder_level"]),
                unit_cost=Decimal(row["unit_cost"]),
                is_active=_as_bool(row["is_active"]),
            ),
        )
        item_ids[item.code] = item.id

    warehouse_ids = {}
    for row in warehouses:
        warehouse = warehouse_service.create_warehouse(
            db,
            WarehouseCreate(
                name=row["name"],
                location=row["location"] or None,
                is_active=_as_bool(row["is_active"]),
            ),
        )
        warehouse_ids[warehouse.name] = warehouse.id

    for row in transactions:
        common = {
            "item_id": item_ids[row["item_code"]],
            "warehouse_id": warehouse_ids[row["warehouse_name"]],
            "quantity": Decimal(row["quantity"]),
            "transaction_date": date.fromisoformat(row["transaction_date"]),
            "remarks": row["remarks"] or None,
        }
        transaction_type = row["transaction_type"].strip().upper()
        if transaction_type == "IN":
            stock_service.stock_in(
                db,
                StockInCreate(
                    **common,
                    unit_cost=Decimal(row["unit_cost"]) if row["unit_cost"] else None,
                    supplier=row["supplier"] or None,
                ),
            )
        else:
            stock_service.stock_out(db, StockOutCreate(**common))

    _verify_balances(db, expected_rows)
    return {
        "items": _table_count(db, Item),
        "warehouses": _table_count(db, Warehouse),
        "transactions": _table_count(db, StockTransaction),
        "verified_balances": len(expected_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the garment sample dataset.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete existing inventory data before loading the dataset",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        counts = seed_dataset(db, reset=args.reset)
        print(
            "Dataset loaded and verified: "
            f"{counts['items']} items, {counts['warehouses']} warehouses, "
            f"{counts['transactions']} transactions, "
            f"{counts['verified_balances']} balances checked."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()