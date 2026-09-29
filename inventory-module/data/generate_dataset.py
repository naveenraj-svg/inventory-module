"""
Generates the garment-industry sample dataset used to seed the Inventory Module.

Run:  python generate_dataset.py
Output (in this folder):
    warehouses.csv, items.csv, stock_transactions.csv, expected_current_stock.csv

The data is modelled on a knitwear / garment unit (yarn -> fabric -> trims ->
packing -> finished goods). It is deterministic (fixed random seed) and every
stock-out is guaranteed never to exceed the stock available at that moment.
"""
import csv
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

random.seed(2026)
OUT = Path(__file__).resolve().parent
START, END = date(2026, 7, 1), date(2026, 9, 28)
RECEIPT_LAST_DAY = date(2026, 9, 22)   # supplier receipts stop here
ISSUE_LAST_DAY = date(2026, 9, 23)     # regular issues stop here
DRAIN_FIRST_DAY = date(2026, 9, 24)    # final issues that bring stock to its target

# --------------------------------------------------------------------------
# Warehouses: (name, location, is_active)
# --------------------------------------------------------------------------
WAREHOUSES = [
    ("Yarn Store", "Spinning Yard, Block A, Tirupur", True),
    ("Fabric Store", "Knitting & Processing, Block B, Tirupur", True),
    ("Trims Store", "Cutting Section, Block C, Tirupur", True),
    ("Packing Store", "Packing Hall, Block D, Tirupur", True),
    ("Finished Goods Store", "Dispatch Yard, Tirupur", True),
    ("Old Godown (Closed)", "Kangayam Road, Tirupur", False),
]

# --------------------------------------------------------------------------
# Items: (code, name, category, uom, reorder_level, unit_cost_INR, home_warehouse)
# --------------------------------------------------------------------------
Y, F, T, P, G = "Yarn Store", "Fabric Store", "Trims Store", "Packing Store", "Finished Goods Store"
ITEMS = [
    # ---- Yarn (KG) ----
    ("YRN001", "Cotton Combed Yarn 30s", "Yarn", "KG", 1500, 285, Y),
    ("YRN002", "Cotton Combed Yarn 40s", "Yarn", "KG", 1200, 305, Y),
    ("YRN003", "Cotton Carded Yarn 20s", "Yarn", "KG", 2000, 240, Y),
    ("YRN004", "Cotton Compact Yarn 34s", "Yarn", "KG", 1000, 298, Y),
    ("YRN005", "Polyester Yarn 150D", "Yarn", "KG", 800, 118, Y),
    ("YRN006", "Viscose Yarn 30s", "Yarn", "KG", 600, 265, Y),
    ("YRN007", "Lycra Spandex Yarn 40D", "Yarn", "KG", 150, 720, Y),
    ("YRN008", "Cotton Slub Yarn 24s", "Yarn", "KG", 800, 268, Y),
    ("YRN009", "Cotton Melange Yarn 30s Grey", "Yarn", "KG", 900, 232, Y),
    ("YRN010", "Organic Cotton Yarn 30s", "Yarn", "KG", 500, 340, Y),
    # ---- Fabric ----
    ("FAB001", "Single Jersey 160 GSM White", "Fabric", "KG", 1200, 345, F),
    ("FAB002", "Single Jersey 180 GSM Navy", "Fabric", "KG", 1200, 362, F),
    ("FAB003", "Single Jersey 180 GSM Black", "Fabric", "KG", 1200, 368, F),
    ("FAB004", "Single Jersey 200 GSM Grey Melange", "Fabric", "KG", 1000, 355, F),
    ("FAB005", "1x1 Rib 220 GSM White", "Fabric", "KG", 600, 372, F),
    ("FAB006", "1x1 Rib 220 GSM Black", "Fabric", "KG", 600, 380, F),
    ("FAB007", "Pique 220 GSM Navy", "Fabric", "KG", 800, 385, F),
    ("FAB008", "Pique 220 GSM White", "Fabric", "KG", 800, 375, F),
    ("FAB009", "Fleece 280 GSM Grey Melange", "Fabric", "KG", 1000, 395, F),
    ("FAB010", "Fleece 300 GSM Black", "Fabric", "KG", 1000, 410, F),
    ("FAB011", "French Terry 240 GSM Navy", "Fabric", "KG", 900, 390, F),
    ("FAB012", "Interlock 200 GSM White", "Fabric", "KG", 700, 365, F),
    ("FAB013", "Lycra Jersey 190 GSM Black", "Fabric", "KG", 800, 430, F),
    ("FAB014", "Denim 10 oz Indigo", "Fabric", "MTR", 3000, 215, F),
    ("FAB015", "Denim 12 oz Black", "Fabric", "MTR", 3000, 245, F),
    ("FAB016", "Poplin Shirting 110 GSM White", "Fabric", "MTR", 2500, 128, F),
    ("FAB017", "Twill 180 GSM Khaki", "Fabric", "MTR", 2000, 165, F),
    ("FAB018", "Viscose Rayon Printed", "Fabric", "MTR", 2000, 142, F),
    ("FAB019", "Waffle Knit 200 GSM Beige", "Fabric", "KG", 500, 398, F),
    ("FAB020", "Sherpa Fleece 320 GSM Off-White", "Fabric", "KG", 400, 465, F),
    # ---- Trims ----
    ("TRM001", "Sewing Thread 40/2 White", "Trims", "CONE", 400, 92, T),
    ("TRM002", "Sewing Thread 40/2 Black", "Trims", "CONE", 400, 92, T),
    ("TRM003", "Sewing Thread 40/2 Navy", "Trims", "CONE", 300, 94, T),
    ("TRM004", "Overlock Thread 150D White", "Trims", "CONE", 300, 78, T),
    ("TRM005", "Nylon Zipper 6 inch Black", "Trims", "PCS", 5000, 11, T),
    ("TRM006", "Nylon Zipper 8 inch Navy", "Trims", "PCS", 3000, 13, T),
    ("TRM007", "Metal Zipper 5 inch Brass (Jeans)", "Trims", "PCS", 4000, 16, T),
    ("TRM008", "Poly Button 4-Hole 18L White", "Trims", "PCS", 30000, 0.55, T),
    ("TRM009", "Poly Button 4-Hole 24L Black", "Trims", "PCS", 20000, 0.75, T),
    ("TRM010", "Metal Jeans Button 17 mm", "Trims", "PCS", 15000, 3.2, T),
    ("TRM011", "Elastic 25 mm Black", "Trims", "MTR", 5000, 9.5, T),
    ("TRM012", "Cotton Drawcord 8 mm", "Trims", "MTR", 6000, 4.2, T),
    ("TRM013", "Woven Main Label", "Trims", "PCS", 25000, 0.85, T),
    ("TRM014", "Satin Care Label", "Trims", "PCS", 25000, 0.35, T),
    ("TRM015", "Size Label (S-XXL)", "Trims", "PCS", 20000, 0.30, T),
    ("TRM016", "Fusible Interlining 90 cm", "Trims", "MTR", 3000, 38, T),
    ("TRM017", "Velcro Tape 20 mm", "Trims", "MTR", 2000, 14, T),
    ("TRM018", "Snap Button 15 mm", "Trims", "PCS", 10000, 1.8, T),
    # ---- Packing ----
    ("PKG001", "Poly Bag 10 x 14 inch", "Packing", "PCS", 20000, 1.4, P),
    ("PKG002", "Poly Bag 12 x 16 inch", "Packing", "PCS", 15000, 1.9, P),
    ("PKG003", "Carton 5-Ply 24 x 16 x 12 inch", "Packing", "PCS", 1500, 42, P),
    ("PKG004", "Carton 7-Ply 30 x 20 x 14 inch", "Packing", "PCS", 800, 68, P),
    ("PKG005", "Hang Tag Printed", "Packing", "PCS", 20000, 0.9, P),
    ("PKG006", "Price Sticker Roll", "Packing", "ROLL", 200, 65, P),
    ("PKG007", "Tissue Paper Sheet", "Packing", "PCS", 10000, 0.6, P),
    ("PKG008", "Collar Support Insert", "Packing", "PCS", 12000, 0.45, P),
    ("PKG009", "Packing Tape 2 inch", "Packing", "ROLL", 300, 48, P),
    ("PKG010", "Silica Gel Sachet", "Packing", "PCS", 15000, 0.35, P),
    # ---- Finished goods (cost price per piece) ----
    ("FG001", "Men's Round Neck T-Shirt White", "Finished Goods", "PCS", 3000, 118, G),
    ("FG002", "Men's Polo T-Shirt Navy", "Finished Goods", "PCS", 2000, 205, G),
    ("FG003", "Women's Leggings Black", "Finished Goods", "PCS", 2500, 135, G),
    ("FG004", "Kids Hoodie Grey", "Finished Goods", "PCS", 1200, 260, G),
    ("FG005", "Men's Jogger Track Pant Black", "Finished Goods", "PCS", 1500, 240, G),
    ("FG006", "Men's Denim Jeans Indigo", "Finished Goods", "PCS", 1200, 420, G),
    ("FG007", "Women's Kurti Cotton Printed", "Finished Goods", "PCS", 1000, 190, G),
    ("FG008", "Unisex Sweatshirt Navy", "Finished Goods", "PCS", 1500, 285, G),
]

# An inactive item (kept in the master, but no stock is booked against it)
INACTIVE_ITEM = ("FAB099", "Poplin Shirting 90 GSM Pink (Discontinued)", "Fabric", "MTR", 0, 118, F)

# Some packing items are also kept at the dispatch yard: (code, extra warehouse)
SECOND_LOCATIONS = [("PKG001", G), ("PKG003", G), ("PKG005", G)]

SUPPLIERS = {
    "Yarn": ["Kongu Cotton Yarn Traders", "Annai Spinning Mills", "Balaji Polyester Yarns", "Vel Organic Fibres"],
    "Fabric": ["Perumal Knit Fabrics", "Sakthi Dyeing & Processing", "Coimbatore Denim Works", "Om Sai Fabrics"],
    "Trims": ["Tirupur Trims & Accessories", "Ganesh Thread House", "Universal Zipper Co", "Sri Vinayaga Labels"],
    "Packing": ["Kaveri Packaging Industries", "Srinivasa Carton Works", "Bharath Poly Products"],
    "Finished Goods": ["In-house Production - Unit 1", "In-house Production - Unit 2"],
}
CUSTOMERS = ["Urban Threads Retail", "Northwind Apparel Exports", "Kidz Corner Stores", "Sunrise Fashion Hub"]
ISSUE_TO = {
    "Yarn": "Knitting",
    "Fabric": "Cutting",
    "Trims": "Stitching Line",
    "Packing": "Packing Section",
}

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def granule(uom):
    return Decimal("0.5") if uom in ("KG", "MTR") else Decimal("1")


def lot_step(uom, reorder):
    if uom in ("KG", "MTR"):
        return Decimal("10")
    if uom in ("CONE", "ROLL"):
        return Decimal("10") if reorder >= 300 else Decimal("5")
    if reorder >= 10000:
        return Decimal("500")
    if reorder >= 1000:
        return Decimal("100")
    return Decimal("10")


def issue_step(uom, reorder):
    if uom in ("KG", "MTR"):
        return Decimal("2.5")
    if uom in ("CONE", "ROLL"):
        return Decimal("1")
    return Decimal("50") if reorder >= 10000 else Decimal("10")


def round_to(value, step, minimum=None):
    d = (Decimal(str(value)) / step).to_integral_value() * step
    if minimum is not None and d < minimum:
        d = minimum
    return d


def floor_to(value, step):
    return (Decimal(value) / step).to_integral_value(rounding="ROUND_FLOOR") * step


def rand_date(a, b):
    return a + timedelta(days=random.randint(0, (b - a).days))


def fmt_qty(q, uom):
    return f"{q:.1f}" if uom in ("KG", "MTR") else f"{int(q)}"



def pick_supplier(code, category):
    """Choose a supplier that plausibly makes this kind of item."""
    n = int(code[3:]) if code[:3] in ("YRN", "FAB", "TRM") else 0
    if category == "Yarn":
        if code == "YRN010":
            return "Vel Organic Fibres"
        if code == "YRN005":
            return "Balaji Polyester Yarns"
        return random.choice(["Kongu Cotton Yarn Traders", "Annai Spinning Mills"])
    if category == "Fabric":
        if code in ("FAB014", "FAB015"):
            return "Coimbatore Denim Works"
        if code in ("FAB016", "FAB017", "FAB018"):
            return "Om Sai Fabrics"
        return random.choice(["Perumal Knit Fabrics", "Sakthi Dyeing & Processing"])
    if category == "Trims":
        if 1 <= n <= 4:
            return "Ganesh Thread House"
        if n in (5, 6, 7):
            return "Universal Zipper Co"
        if n in (13, 14, 15):
            return "Sri Vinayaga Labels"
        return "Tirupur Trims & Accessories"
    return random.choice(SUPPLIERS[category])

# --------------------------------------------------------------------------
# simulate one (item, warehouse) stock history
# --------------------------------------------------------------------------
def simulate(item, warehouse, target_ratio, lot_mult, n_in, n_out, in_house=False):
    code, name, category, uom, reorder, cost, _ = item
    reorder = Decimal(str(reorder))
    lstep, istep, g = lot_step(uom, reorder), issue_step(uom, reorder), granule(uom)
    events = []  # dicts: date, type, qty, unit_cost, supplier

    # receipts
    first_day = START + timedelta(days=random.randint(0, 6))
    dates = [first_day] + sorted(
        rand_date(START + timedelta(days=10), RECEIPT_LAST_DAY) for _ in range(n_in - 1)
    )
    total_in = Decimal(0)
    for i, d in enumerate(dates):
        mult = lot_mult * (1.4 if i == 0 else 1.0) * random.uniform(0.7, 1.3)
        qty = round_to(reorder * Decimal(str(round(mult, 3))), lstep, minimum=lstep)
        unit_cost = (Decimal(str(cost)) * Decimal(str(round(random.uniform(0.96, 1.05), 4)))).quantize(
            Decimal("0.01")
        )
        events.append(
            {
                "date": d,
                "type": "IN",
                "qty": qty,
                "unit_cost": unit_cost,
                "supplier": pick_supplier(code, category),
                "opening": i == 0 and not in_house,
            }
        )
        total_in += qty

    target = round_to(reorder * Decimal(str(round(target_ratio, 3))), g) if target_ratio > 0 else Decimal(0)
    to_issue = max(total_in - target, Decimal(0))

    # regular issues
    for _ in range(n_out):
        d = rand_date(first_day + timedelta(days=1), ISSUE_LAST_DAY)
        chunk = to_issue / n_out * Decimal(str(round(random.uniform(0.5, 1.5), 3)))
        events.append({"date": d, "type": "OUT", "qty": round_to(chunk, istep, minimum=istep)})

    # walk chronologically (IN before OUT on the same day) and never overdraw
    events.sort(key=lambda e: (e["date"], 0 if e["type"] == "IN" else 1))
    balance, final = Decimal(0), []
    for e in events:
        if e["type"] == "IN":
            balance += e["qty"]
            final.append(e)
            continue
        qty = e["qty"]
        if qty > balance:
            qty = floor_to(balance * Decimal(str(round(random.uniform(0.5, 0.9), 3))), istep)
        if qty <= 0:
            continue
        e["qty"] = qty
        balance -= qty
        final.append(e)

    # final issues so stock ends close to the intended level
    drain = balance - target
    if drain > 0:
        if target > 0:
            drain = floor_to(drain, istep)
        if drain > 0:
            p1 = floor_to(drain * Decimal(str(round(random.uniform(0.3, 0.6), 3))), istep)
            parts = [p for p in (p1, drain - p1) if p > 0]
            for p in parts:
                final.append(
                    {"date": rand_date(DRAIN_FIRST_DAY, END), "type": "OUT", "qty": p}
                )

    for e in final:
        e.update(item_code=code, warehouse=warehouse, uom=uom, category=category, in_house=in_house)
    return final


# --------------------------------------------------------------------------
# build everything
# --------------------------------------------------------------------------
def build():
    low_pool = [i[0] for i in ITEMS if i[2] != "Finished Goods"] + [i[0] for i in ITEMS if i[2] == "Finished Goods"]
    zero_items = set(random.sample(low_pool, 2))
    low_items = set(random.sample([c for c in low_pool if c not in zero_items], 14))

    transactions = []
    by_code = {i[0]: i for i in ITEMS}

    for item in ITEMS:
        code, _, category, uom, reorder, cost, wh = item
        fg = category == "Finished Goods"
        if code in zero_items:
            ratio = 0.0
        elif code in low_items:
            ratio = random.uniform(0.15, 0.95)
        else:
            ratio = random.uniform(1.3, 3.5)
        transactions += simulate(
            item,
            wh,
            target_ratio=ratio,
            lot_mult=random.uniform(0.6, 1.4) if fg else random.uniform(1.5, 3.2),
            n_in=random.randint(5, 9) if fg else random.randint(3, 6),
            n_out=random.randint(8, 18) if fg else random.randint(10, 26),
            in_house=fg,
        )

    for code, extra_wh in SECOND_LOCATIONS:
        transactions += simulate(
            by_code[code],
            extra_wh,
            target_ratio=random.uniform(1.1, 1.8),
            lot_mult=random.uniform(1.0, 1.6),
            n_in=random.randint(2, 4),
            n_out=random.randint(5, 10),
        )

    # global order: date, IN before OUT, then item
    transactions.sort(key=lambda e: (e["date"], 0 if e["type"] == "IN" else 1, e["item_code"], e["warehouse"]))

    # document numbers / remarks
    grn = iss = 0
    for e in transactions:
        if e["type"] == "IN":
            grn += 1
            if e["opening"]:
                e["remarks"] = f"Opening stock - GRN-2026-{grn:04d}"
            elif e["in_house"]:
                e["remarks"] = f"Finished lot received from production - GRN-2026-{grn:04d}"
            else:
                e["remarks"] = f"GRN-2026-{grn:04d} against PO-{random.randint(1000, 1999)}"
        else:
            iss += 1
            if e["category"] == "Finished Goods":
                e["remarks"] = f"Dispatch to {random.choice(CUSTOMERS)} - DC-2026-{iss:04d}"
            else:
                line = ISSUE_TO[e["category"]]
                if line == "Stitching Line":
                    line += f" {random.randint(1, 8)}"
                e["remarks"] = f"Issued to {line} - ISS-2026-{iss:04d}"
    return transactions


def write_csvs(transactions):
    wh_names = {w[0] for w in WAREHOUSES}
    with open(OUT / "warehouses.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "location", "is_active"])
        for name, loc, active in WAREHOUSES:
            w.writerow([name, loc, str(active).lower()])

    all_items = ITEMS + [INACTIVE_ITEM]
    with open(OUT / "items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["code", "name", "category", "uom", "reorder_level", "unit_cost", "is_active"])
        for code, name, cat, uom, reorder, cost, _ in sorted(all_items, key=lambda i: i[0]):
            w.writerow([code, name, cat, uom, reorder, f"{Decimal(str(cost)):.2f}", str(code != INACTIVE_ITEM[0]).lower()])

    with open(OUT / "stock_transactions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["transaction_date", "transaction_type", "item_code", "warehouse_name",
             "quantity", "unit_cost", "supplier", "remarks"]
        )
        for e in transactions:
            assert e["warehouse"] in wh_names
            w.writerow(
                [
                    e["date"].isoformat(),
                    e["type"],
                    e["item_code"],
                    e["warehouse"],
                    fmt_qty(e["qty"], e["uom"]),
                    f"{e['unit_cost']:.2f}" if e["type"] == "IN" else "",
                    e.get("supplier", "") if e["type"] == "IN" else "",
                    e["remarks"],
                ]
            )

    # expected result of loading the data (used by the seed script to self-check)
    items = {i[0]: i for i in all_items}
    balances = {}
    for e in transactions:
        key = (e["item_code"], e["warehouse"])
        balances[key] = balances.get(key, Decimal(0)) + (e["qty"] if e["type"] == "IN" else -e["qty"])
    with open(OUT / "expected_current_stock.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_code", "item_name", "warehouse_name", "quantity", "uom", "reorder_level", "status"])
        for (code, wh), qty in sorted(balances.items()):
            _, name, _, uom, reorder, _, _ = items[code]
            status = "LOW" if qty <= Decimal(str(reorder)) else "NORMAL"
            w.writerow([code, name, wh, fmt_qty(qty, uom), uom, reorder, status])
    return balances


if __name__ == "__main__":
    tx = build()
    balances = write_csvs(tx)
    low = sum(
        1
        for (code, _), q in balances.items()
        if q <= Decimal(str({i[0]: i[4] for i in ITEMS}[code]))
    )
    print(f"warehouses: {len(WAREHOUSES)}  items: {len(ITEMS) + 1}  transactions: {len(tx)}")
    print(f"stock lines: {len(balances)}  low-stock lines: {low}")
