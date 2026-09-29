import csv
import io
from typing import Iterable

HEADERS = [
    "Item Code",
    "Item",
    "Category",
    "Warehouse",
    "Current Qty",
    "UOM",
    "Reorder Level",
    "Status",
]


def _safe(value) -> str:
    """Neutralise spreadsheet formula injection (=, +, -, @ at the start)."""
    text = "" if value is None else str(value)
    if text and text[0] in ("=", "+", "-", "@"):
        return "'" + text
    return text


def _num(value) -> str:
    number = float(value)
    return str(int(number)) if number.is_integer() else f"{number:g}"


def current_stock_to_csv(rows: Iterable[dict]) -> str:
    """Turn the current-stock rows into CSV text."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(HEADERS)
    for r in rows:
        writer.writerow(
            [
                _safe(r["item_code"]),
                _safe(r["item_name"]),
                _safe(r["category"]),
                _safe(r["warehouse_name"]),
                _num(r["quantity"]),
                _safe(r["uom"]),
                _num(r["reorder_level"]),
                r["status"],
            ]
        )
    return buffer.getvalue()
