from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.warehouse import WarehouseCreate, WarehouseResponse
from app.services import warehouse_service

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("", response_model=list[WarehouseResponse])
def list_warehouses(active_only: bool = False, db: Session = Depends(get_db)):
    return warehouse_service.list_warehouses(db, active_only)


@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db)):
    return warehouse_service.create_warehouse(db, payload)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    return warehouse_service.get_warehouse(db, warehouse_id)
