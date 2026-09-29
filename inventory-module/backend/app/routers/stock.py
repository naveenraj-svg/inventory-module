from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.stock import (
    AvailableStockResponse,
    CurrentStockRow,
    StockInCreate,
    StockOutCreate,
    StockSummary,
    TransactionResponse,
)
from app.services import item_service, stock_service, warehouse_service
from app.utils.csv_export import current_stock_to_csv

router = APIRouter(tags=["Stock"])


def _tx_response(db: Session, tx) -> dict:
    return stock_service.transaction_to_dict(
        tx,
        item_service.get_item(db, tx.item_id),
        warehouse_service.get_warehouse(db, tx.warehouse_id),
    )


@router.post(
    "/stock-in",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def stock_in(payload: StockInCreate, db: Session = Depends(get_db)):
    return _tx_response(db, stock_service.stock_in(db, payload))


@router.post(
    "/stock-out",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def stock_out(payload: StockOutCreate, db: Session = Depends(get_db)):
    return _tx_response(db, stock_service.stock_out(db, payload))


@router.get("/stock/current", response_model=list[CurrentStockRow])
def current_stock(
    warehouse_id: int | None = None,
    item_id: int | None = None,
    q: str | None = None,
    low_only: bool = False,
    db: Session = Depends(get_db),
):
    return stock_service.get_current_stock(db, warehouse_id, item_id, q, low_only)


@router.get("/stock/current/export")
def export_current_stock(
    warehouse_id: int | None = None,
    item_id: int | None = None,
    q: str | None = None,
    low_only: bool = False,
    db: Session = Depends(get_db),
):
    rows = stock_service.get_current_stock(db, warehouse_id, item_id, q, low_only)
    content = current_stock_to_csv(rows)
    filename = f"current-stock-{date.today().isoformat()}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/stock/available", response_model=AvailableStockResponse)
def available_stock(
    item_id: int = Query(gt=0),
    warehouse_id: int = Query(gt=0),
    db: Session = Depends(get_db),
):
    item = item_service.get_item(db, item_id)
    warehouse_service.get_warehouse(db, warehouse_id)
    return {
        "item_id": item_id,
        "warehouse_id": warehouse_id,
        "uom": item.uom,
        "available": stock_service.get_available_quantity(db, item_id, warehouse_id),
    }


@router.get("/stock/transactions", response_model=list[TransactionResponse])
def transactions(
    item_id: int | None = None,
    warehouse_id: int | None = None,
    transaction_type: Literal["IN", "OUT"] | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return stock_service.list_transactions(
        db, item_id, warehouse_id, transaction_type, limit
    )


@router.get("/stock/summary", response_model=StockSummary)
def summary(db: Session = Depends(get_db)):
    return stock_service.get_summary(db)
