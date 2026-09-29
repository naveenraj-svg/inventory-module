from decimal import Decimal

from sqlalchemy import case, func, select, true
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, InsufficientStockError
from app.models.item import Item
from app.models.stock_transaction import IN, OUT, StockTransaction
from app.models.warehouse import Warehouse
from app.schemas.stock import StockInCreate, StockOutCreate
from app.services import item_service, warehouse_service

ZERO = Decimal("0")


def _signed_quantity():
    """IN adds to stock, OUT subtracts from it."""
    return case(
        (StockTransaction.transaction_type == IN, StockTransaction.quantity),
        else_=-StockTransaction.quantity,
    )


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f") if value != 0 else "0"


# ------------------------------------------------------------------ #
# Availability
# ------------------------------------------------------------------ #
def get_available_quantity(db: Session, item_id: int, warehouse_id: int) -> Decimal:
    """Current Stock = Total Stock In - Total Stock Out."""
    total = db.scalar(
        select(func.coalesce(func.sum(_signed_quantity()), 0)).where(
            StockTransaction.item_id == item_id,
            StockTransaction.warehouse_id == warehouse_id,
        )
    )
    return Decimal(str(total or 0))


# ------------------------------------------------------------------ #
# Stock in / out
# ------------------------------------------------------------------ #
def _validate_master_data(db: Session, item_id: int, warehouse_id: int) -> Item:
    item = item_service.get_item(db, item_id)
    warehouse = warehouse_service.get_warehouse(db, warehouse_id)
    if not item.is_active:
        raise BusinessRuleError(f"Item '{item.code}' is inactive.")
    if not warehouse.is_active:
        raise BusinessRuleError(f"Warehouse '{warehouse.name}' is inactive.")
    return item


def stock_in(db: Session, data: StockInCreate) -> StockTransaction:
    item = _validate_master_data(db, data.item_id, data.warehouse_id)

    tx = StockTransaction(
        item_id=data.item_id,
        warehouse_id=data.warehouse_id,
        transaction_type=IN,
        quantity=data.quantity,
        # Fall back to the item's standard cost when none is given
        unit_cost=data.unit_cost if data.unit_cost is not None else item.unit_cost,
        supplier=data.supplier,
        transaction_date=data.transaction_date,
        remarks=data.remarks,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def stock_out(db: Session, data: StockOutCreate) -> StockTransaction:
    item = _validate_master_data(db, data.item_id, data.warehouse_id)

    # Lock the item row so two concurrent stock-outs of the same item are
    # processed one after the other (no-op on SQLite, real lock on PostgreSQL).
    db.execute(select(Item.id).where(Item.id == item.id).with_for_update())

    available = get_available_quantity(db, data.item_id, data.warehouse_id)
    if data.quantity > available:
        db.rollback()
        raise InsufficientStockError(
            f"Insufficient stock. Available: {_fmt(available)} {item.uom}, "
            f"requested: {_fmt(data.quantity)} {item.uom}."
        )

    tx = StockTransaction(
        item_id=data.item_id,
        warehouse_id=data.warehouse_id,
        transaction_type=OUT,
        quantity=data.quantity,
        transaction_date=data.transaction_date,
        remarks=data.remarks,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


# ------------------------------------------------------------------ #
# Reports
# ------------------------------------------------------------------ #
def _current_stock_query(
    warehouse_id: int | None = None,
    item_id: int | None = None,
    q: str | None = None,
):
    qty = func.coalesce(func.sum(_signed_quantity()), 0).label("quantity")
    stmt = (
        select(
            Item.id.label("item_id"),
            Item.code.label("item_code"),
            Item.name.label("item_name"),
            Item.category.label("category"),
            Item.uom.label("uom"),
            Item.reorder_level.label("reorder_level"),
            Warehouse.id.label("warehouse_id"),
            Warehouse.name.label("warehouse_name"),
            qty,
        )
        .select_from(Item)
        .join(Warehouse, true())
        .outerjoin(
            StockTransaction,
            (StockTransaction.item_id == Item.id)
            & (StockTransaction.warehouse_id == Warehouse.id),
        )
        .group_by(
            Item.id,
            Item.code,
            Item.name,
            Item.category,
            Item.uom,
            Item.reorder_level,
            Warehouse.id,
            Warehouse.name,
        )
        .order_by(Item.code, Warehouse.name)
    )
    if warehouse_id is not None:
        stmt = stmt.where(Warehouse.id == warehouse_id)
    if item_id is not None:
        stmt = stmt.where(Item.id == item_id)
    if q:
        cleaned = q.strip()
        if cleaned:
            like = f"%{cleaned}%"
            stmt = stmt.where(Item.code.ilike(like) | Item.name.ilike(like))
    return stmt


def get_current_stock(
    db: Session,
    warehouse_id: int | None = None,
    item_id: int | None = None,
    q: str | None = None,
    low_only: bool = False,
) -> list[dict]:
    rows = []
    for r in db.execute(_current_stock_query(warehouse_id, item_id, q)):
        quantity = Decimal(str(r.quantity or 0))
        reorder = Decimal(str(r.reorder_level or 0))
        status = "LOW" if quantity <= reorder else "NORMAL"
        if low_only and status != "LOW":
            continue
        rows.append(
            {
                "item_id": r.item_id,
                "item_code": r.item_code,
                "item_name": r.item_name,
                "category": r.category,
                "warehouse_id": r.warehouse_id,
                "warehouse_name": r.warehouse_name,
                "uom": r.uom,
                "quantity": quantity,
                "reorder_level": reorder,
                "status": status,
            }
        )
    return rows


def list_transactions(
    db: Session,
    item_id: int | None = None,
    warehouse_id: int | None = None,
    transaction_type: str | None = None,
    limit: int = 100,
) -> list[dict]:
    stmt = (
        select(StockTransaction, Item, Warehouse)
        .join(Item, Item.id == StockTransaction.item_id)
        .join(Warehouse, Warehouse.id == StockTransaction.warehouse_id)
        .order_by(
            StockTransaction.transaction_date.desc(), StockTransaction.id.desc()
        )
        .limit(limit)
    )
    if item_id:
        stmt = stmt.where(StockTransaction.item_id == item_id)
    if warehouse_id:
        stmt = stmt.where(StockTransaction.warehouse_id == warehouse_id)
    if transaction_type:
        stmt = stmt.where(StockTransaction.transaction_type == transaction_type)

    return [
        transaction_to_dict(tx, item, warehouse)
        for tx, item, warehouse in db.execute(stmt)
    ]


def transaction_to_dict(tx: StockTransaction, item: Item, warehouse: Warehouse) -> dict:
    return {
        "id": tx.id,
        "item_id": tx.item_id,
        "item_code": item.code,
        "item_name": item.name,
        "warehouse_id": tx.warehouse_id,
        "warehouse_name": warehouse.name,
        "uom": item.uom,
        "transaction_type": tx.transaction_type,
        "quantity": tx.quantity,
        "unit_cost": tx.unit_cost,
        "supplier": tx.supplier,
        "transaction_date": tx.transaction_date,
        "remarks": tx.remarks,
        "created_at": tx.created_at,
    }


def get_summary(db: Session) -> dict:
    return {
        "total_items": db.scalar(select(func.count(Item.id))) or 0,
        "total_warehouses": db.scalar(select(func.count(Warehouse.id))) or 0,
        "low_stock_count": len(get_current_stock(db, low_only=True)),
        "total_transactions": db.scalar(select(func.count(StockTransaction.id))) or 0,
    }
