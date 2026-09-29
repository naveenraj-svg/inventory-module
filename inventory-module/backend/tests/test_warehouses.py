def test_create_and_list_warehouses(client):
    res = client.post("/warehouses", json={"name": "Yarn Store", "location": "Block B"})
    assert res.status_code == 201
    assert res.json()["is_active"] is True

    res = client.get("/warehouses")
    assert res.status_code == 200
    assert [w["name"] for w in res.json()] == ["Yarn Store"]


def test_duplicate_warehouse_name_is_rejected(client, warehouse):
    res = client.post("/warehouses", json={"name": "fabric store"})
    assert res.status_code == 409


def test_blank_name_is_rejected(client):
    assert client.post("/warehouses", json={"name": "   "}).status_code == 422


def test_get_missing_warehouse_returns_404(client):
    assert client.get("/warehouses/999").status_code == 404
