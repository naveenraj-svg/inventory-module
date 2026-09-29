import { useEffect, useState } from "react";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Table from "../components/Table";
import useApi from "../hooks/useApi";
import { getCurrentStock, getWarehouses } from "../services/api";
import { exportCurrentStockCsv } from "../utils/exportCsv";
import { formatNumber } from "../utils/format";

export const STOCK_COLUMNS = [
  { key: "item", header: "Item", render: (r) => (<><strong>{r.item_code}</strong> {r.item_name}</>) },
  { key: "warehouse_name", header: "Warehouse" },
  { key: "quantity", header: "Qty", align: "right", render: (r) => formatNumber(r.quantity) },
  { key: "uom", header: "UOM" },
  { key: "reorder_level", header: "Reorder level", align: "right", render: (r) => formatNumber(r.reorder_level) },
  { key: "status", header: "Status", render: (r) => <Badge value={r.status} /> },
];

export const stockRowKey = (r) => `${r.item_id}-${r.warehouse_id}`;
export const stockRowClass = (r) => (r.status === "LOW" ? "row-low" : "");

export default function CurrentStock() {
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [warehouseId, setWarehouseId] = useState("");
  const [lowOnly, setLowOnly] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");

  useEffect(() => {
    const t = setTimeout(() => setQuery(search.trim()), 250);
    return () => clearTimeout(t);
  }, [search]);

  const filters = { q: query, warehouse_id: warehouseId, low_only: lowOnly };
  const stock = useApi(getCurrentStock, [filters]);
  const warehouses = useApi(getWarehouses, []);

  const handleExport = async () => {
    setExporting(true);
    setExportError("");
    try {
      await exportCurrentStockCsv(filters);
    } catch (err) {
      setExportError(err.message);
    } finally {
      setExporting(false);
    }
  };

  return (
    <section>
      <div className="page-head">
        <div>
          <h1>Current stock</h1>
          <p className="page-sub">Total stock in minus total stock out, per item and warehouse.</p>
        </div>
        <Button variant="secondary" onClick={handleExport} loading={exporting}>Export CSV</Button>
      </div>

      <Alert>{stock.error || exportError}</Alert>

      <div className="toolbar">
        <input type="search" className="input" placeholder="Search by code or name" aria-label="Search stock"
          value={search} onChange={(e) => setSearch(e.target.value)} />
        <select className="input" aria-label="Filter by warehouse" value={warehouseId}
          onChange={(e) => setWarehouseId(e.target.value)}>
          <option value="">All warehouses</option>
          {(warehouses.data || []).map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>
        <label className="check">
          <input type="checkbox" checked={lowOnly} onChange={(e) => setLowOnly(e.target.checked)} />
          Low stock only
        </label>
      </div>

      <Table
        columns={STOCK_COLUMNS}
        rows={stock.data}
        rowKey={stockRowKey}
        rowClassName={stockRowClass}
        loading={stock.loading}
        emptyMessage={lowOnly ? "Nothing is running low." : "No stock recorded yet. Record a stock in first."}
      />
    </section>
  );
}
