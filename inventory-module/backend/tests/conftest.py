import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database.base import Base
from app.database.connection import get_db
from app.main import app


@pytest.fixture()
def client():
    """A test client backed by a throw-away in-memory SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def item(client):
    res = client.post(
        "/items",
        json={
            "code": "fab001",
            "name": "Cotton Fabric",
            "category": "Fabric",
            "uom": "kg",
            "reorder_level": 100,
            "unit_cost": 250,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()


@pytest.fixture()
def warehouse(client):
    res = client.post("/warehouses", json={"name": "Fabric Store", "location": "Block A"})
    assert res.status_code == 201, res.text
    return res.json()
