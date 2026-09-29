import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app import main as app_main
from app.database.base import Base
from app.models.item import Item
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from scripts.seed import seed_dataset


def test_seed_dataset_loads_all_modules_and_matches_expected_balances():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = session_factory()
    try:
        counts = seed_dataset(db)
        assert counts == {
            "items": 67,
            "warehouses": 6,
            "transactions": 1612,
            "verified_balances": 69,
        }
        with pytest.raises(RuntimeError, match="Use --reset"):
            seed_dataset(db)
    finally:
        db.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_local_startup_creates_and_seeds_empty_database(tmp_path, monkeypatch, capsys):
    engine = create_engine(f"sqlite:///{tmp_path / 'startup.db'}")
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(app_main, "engine", engine)
    monkeypatch.setattr(app_main, "SessionLocal", session_factory)

    try:
        app_main.initialize_local_database()
        with session_factory() as db:
            counts = tuple(
                db.scalar(select(func.count()).select_from(model))
                for model in (Item, Warehouse, StockTransaction)
            )
        assert counts == (67, 6, 1612)
        assert "Sample dataset loaded and verified" in capsys.readouterr().out
    finally:
        engine.dispose()
