def test_create_item_normalises_code_and_uom(client):
    res = client.post(
        "/items",
        json={"code": " fab001 ", "name": " Cotton Fabric ", "uom": "kg"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["code"] == "FAB001"
    assert body["uom"] == "KG"
    assert body["name"] == "Cotton Fabric"
    assert body["reorder_level"] == 0
    assert body["is_active"] is True


def test_list_and_get_items(client, item):
    res = client.get("/items")
    assert res.status_code == 200
    assert [i["code"] for i in res.json()] == ["FAB001"]

    res = client.get(f"/items/{item['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "Cotton Fabric"


def test_search_items(client, item):
    assert len(client.get("/items", params={"q": "cotton"}).json()) == 1
    assert client.get("/items", params={"q": "zzz"}).json() == []


def test_get_missing_item_returns_404(client):
    assert client.get("/items/999").status_code == 404


def test_duplicate_code_is_rejected(client, item):
    res = client.post("/items", json={"code": "FAB001", "name": "Other", "uom": "KG"})
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"]


def test_duplicate_code_is_case_insensitive(client, item):
    res = client.post("/items", json={"code": "fab001", "name": "Other", "uom": "KG"})
    assert res.status_code == 409


def test_invalid_values_are_rejected(client):
    base = {"code": "X1", "name": "Thing", "uom": "PCS"}
    assert client.post("/items", json={**base, "unit_cost": -1}).status_code == 422
    assert client.post("/items", json={**base, "reorder_level": -5}).status_code == 422
    assert client.post("/items", json={**base, "code": ""}).status_code == 422
    assert client.post("/items", json={**base, "name": ""}).status_code == 422
    assert client.post("/items", json={"code": "X2", "name": "No uom"}).status_code == 422
