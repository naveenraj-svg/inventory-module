def _in(client, item, warehouse, qty, **extra):
    return client.post(
        "/stock-in",
        json={"item_id": item["id"], "warehouse_id": warehouse["id"], "quantity": qty, **extra},
    )


def _out(client, item, warehouse, qty, **extra):
    return client.post(
        "/stock-out",
        json={"item_id": item["id"], "warehouse_id": warehouse["id"], "quantity": qty, **extra},
    )


def _current(client, **params):
    res = client.get("/stock/current", params=params)
    assert res.status_code == 200
    return res.json()


def test_stock_in_creates_transaction(client, item, warehouse):
    res = _in(client, item, warehouse, 500, supplier="ABC Textiles", unit_cost=240)
    assert res.status_code == 201
    body = res.json()
    assert body["transaction_type"] == "IN"
    assert body["quantity"] == 500
    assert body["item_code"] == "FAB001"
    assert body["warehouse_name"] == "Fabric Store"
    assert body["supplier"] == "ABC Textiles"


def test_stock_in_defaults_to_item_cost(client, item, warehouse):
    body = _in(client, item, warehouse, 10).json()
    assert body["unit_cost"] == 250


def test_stock_in_rejects_bad_quantity(client, item, warehouse):
    assert _in(client, item, warehouse, 0).status_code == 422
    assert _in(client, item, warehouse, -5).status_code == 422


def test_stock_in_unknown_item_or_warehouse(client, item, warehouse):
    res = client.post("/stock-in", json={"item_id": 999, "warehouse_id": warehouse["id"], "quantity": 1})
    assert res.status_code == 404
    res = client.post("/stock-in", json={"item_id": item["id"], "warehouse_id": 999, "quantity": 1})
    assert res.status_code == 404


def test_current_stock_is_in_minus_out(client, item, warehouse):
    _in(client, item, warehouse, 500)
    _in(client, item, warehouse, 100)
    assert _out(client, item, warehouse, 200).status_code == 201

    rows = _current(client)
    assert len(rows) == 1
    assert rows[0]["quantity"] == 400
    assert rows[0]["status"] == "NORMAL"


def test_current_stock_includes_zero_balance_rows(client, item, warehouse):
    rows = _current(client, item_id=item["id"], warehouse_id=warehouse["id"])
    assert len(rows) == 1
    assert rows[0]["quantity"] == 0
    assert rows[0]["status"] == "LOW"


def test_stock_out_cannot_exceed_available(client, item, warehouse):
    _in(client, item, warehouse, 50)
    res = _out(client, item, warehouse, 70)
    assert res.status_code == 422
    assert "Insufficient stock" in res.json()["detail"]
    # Nothing must have been recorded
    assert _current(client)[0]["quantity"] == 50


def test_stock_out_with_no_stock_is_rejected(client, item, warehouse):
    assert _out(client, item, warehouse, 1).status_code == 422


def test_stock_out_exact_balance_is_allowed(client, item, warehouse):
    _in(client, item, warehouse, 50)
    assert _out(client, item, warehouse, 50).status_code == 201
    assert _current(client)[0]["quantity"] == 0


def test_stock_is_tracked_per_warehouse(client, item, warehouse):
    other = client.post("/warehouses", json={"name": "Yarn Store"}).json()
    _in(client, item, warehouse, 100)
    # The other warehouse has nothing, so stock-out must fail there
    assert _out(client, item, other, 10).status_code == 422
    assert _out(client, item, warehouse, 10).status_code == 201


def test_available_endpoint(client, item, warehouse):
    _in(client, item, warehouse, 80)
    _out(client, item, warehouse, 30)
    res = client.get(
        "/stock/available",
        params={"item_id": item["id"], "warehouse_id": warehouse["id"]},
    )
    assert res.status_code == 200
    assert res.json()["available"] == 50
    assert res.json()["uom"] == "KG"


def test_low_stock_flag_and_filter(client, item, warehouse):
    _in(client, item, warehouse, 80)  # reorder level is 100 -> LOW
    rows = _current(client)
    assert rows[0]["status"] == "LOW"
    assert len(_current(client, low_only=True)) == 1

    _in(client, item, warehouse, 100)  # 180 -> NORMAL
    assert _current(client)[0]["status"] == "NORMAL"
    assert _current(client, low_only=True) == []


def test_transactions_history(client, item, warehouse):
    _in(client, item, warehouse, 100)
    _out(client, item, warehouse, 10)
    res = client.get("/stock/transactions")
    assert res.status_code == 200
    assert len(res.json()) == 2
    only_out = client.get("/stock/transactions", params={"transaction_type": "OUT"}).json()
    assert [t["transaction_type"] for t in only_out] == ["OUT"]


def test_summary(client, item, warehouse):
    _in(client, item, warehouse, 10)
    body = client.get("/stock/summary").json()
    assert body == {
        "total_items": 1,
        "total_warehouses": 1,
        "low_stock_count": 1,
        "total_transactions": 1,
    }


def test_csv_export(client, item, warehouse):
    _in(client, item, warehouse, 400)
    res = client.get("/stock/current/export")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    assert "attachment" in res.headers["content-disposition"]
    lines = res.text.strip().splitlines()
    assert lines[0].startswith("Item Code,Item,Category,Warehouse,Current Qty")
    assert lines[1].startswith("FAB001,Cotton Fabric,Fabric,Fabric Store,400,KG,100,NORMAL")


def test_csv_export_neutralises_formulas():
    from app.utils.csv_export import current_stock_to_csv

    row = {
        "item_code": "X",
        "item_name": "=HYPERLINK(\"http://evil\")",
        "category": None,
        "warehouse_name": "W",
        "quantity": 1,
        "uom": "PCS",
        "reorder_level": 0,
        "status": "LOW",
    }
    assert "'=HYPERLINK" in current_stock_to_csv([row])
