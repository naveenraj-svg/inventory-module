from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from app import models  # noqa: F401  (register models on Base.metadata)
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.database.base import Base
from app.database.connection import SessionLocal, engine
from app.models.item import Item
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.routers import items, stock, warehouses
from scripts.seed import seed_dataset


def initialize_local_database():
    if engine.dialect.name != "sqlite":
        return

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        counts = [
            db.scalar(select(func.count()).select_from(model)) or 0
            for model in (Item, Warehouse, StockTransaction)
        ]
        if not any(counts):
            seeded = seed_dataset(db)
            print(
                "Sample dataset loaded and verified: "
                f"{seeded['items']:,} items, "
                f"{seeded['warehouses']:,} warehouses, "
                f"{seeded['transactions']:,} transactions, "
                f"{seeded['verified_balances']:,} balances checked."
            )
        else:
            print(
                "Local SQLite dataset ready: "
                f"{counts[0]:,} items, {counts[1]:,} warehouses, "
                f"{counts[2]:,} transactions."
            )


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_local_database()
    yield


app = FastAPI(
    title="Inventory Module API",
    description="Item master, warehouses, stock in/out and current stock.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

register_exception_handlers(app)

app.include_router(items.router)
app.include_router(warehouses.router)
app.include_router(stock.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
