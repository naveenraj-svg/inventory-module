from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate


def list_warehouses(db: Session, active_only: bool = False) -> list[Warehouse]:
    stmt = select(Warehouse).order_by(Warehouse.name)
    if active_only:
        stmt = stmt.where(Warehouse.is_active.is_(True))
    return list(db.scalars(stmt))


def get_warehouse(db: Session, warehouse_id: int) -> Warehouse:
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise NotFoundError(f"Warehouse {warehouse_id} was not found.")
    return warehouse


def create_warehouse(db: Session, data: WarehouseCreate) -> Warehouse:
    exists = db.scalar(
        select(Warehouse.id).where(func.lower(Warehouse.name) == data.name.lower())
    )
    if exists:
        raise ConflictError(f"A warehouse named '{data.name}' already exists.")

    warehouse = Warehouse(**data.model_dump())
    db.add(warehouse)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(f"A warehouse named '{data.name}' already exists.")
    db.refresh(warehouse)
    return warehouse
