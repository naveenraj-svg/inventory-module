from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.item import Item
from app.schemas.item import ItemCreate


def list_items(
    db: Session,
    q: str | None = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 200,
) -> list[Item]:
    stmt = select(Item).order_by(Item.code)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Item.code.ilike(like), Item.name.ilike(like)))
    if active_only:
        stmt = stmt.where(Item.is_active.is_(True))
    return list(db.scalars(stmt.offset(skip).limit(limit)))


def get_item(db: Session, item_id: int) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} was not found.")
    return item


def create_item(db: Session, data: ItemCreate) -> Item:
    exists = db.scalar(select(Item.id).where(Item.code == data.code))
    if exists:
        raise ConflictError(f"An item with code '{data.code}' already exists.")

    item = Item(**data.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        # Two requests raced to create the same code
        db.rollback()
        raise ConflictError(f"An item with code '{data.code}' already exists.")
    db.refresh(item)
    return item
