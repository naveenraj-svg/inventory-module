import { useState } from "react";
import Alert from "../components/Alert";
import Table from "../components/Table";
import StockInForm from "../forms/StockInForm";
import useApi from "../hooks/useApi";
import { getItems, getTransactions, getWarehouses, stockIn } from "../services/api";
import { formatDate, formatMoney, formatNumber } from "../utils/format";

const COLUMNS = [
  { key: "transaction_date", header: "Date", render: (r) => formatDate(r.transaction_date) },
  { key: "item", header: "Item", render: (r) => `${r.item_code} – ${r.item_name}` },
  { key: "warehouse_name", header: "Warehouse" },
  { key: "quantity", header: "Quantity", align: "right", render: (r) => `${formatNumber(r.quantity)} ${r.uom}` },
  { key: "unit_cost", header: "Unit cost", align: "right", render: (r) => formatMoney(r.unit_cost) },
  { key: "supplier", header: "Supplier" },
];

export default function StockIn() {
  const [notice, setNotice] = useState("");
  const items = useApi(getItems, [{ active_only: true, limit: 500 }]);
  const warehouses = useApi(getWarehouses, [{ active_only: true }]);
  const history = useApi(getTransactions, [{ transaction_type: "IN", limit: 10 }]);

  const handleSubmit = async (payload) => {
    const tx = await stockIn(payload);
    setNotice(`Added ${formatNumber(tx.quantity)} ${tx.uom} of ${tx.item_code} to ${tx.warehouse_name}.`);
    history.reload();
  };

  const noMasterData =
    !items.loading && !warehouses.loading && (!items.data?.length || !warehouses.data?.length);

  return (
    <section>
      <div className="page-head">
        <div>
          <h1>Stock in</h1>
          <p className="page-sub">Record goods received into a warehouse.</p>
        </div>
      </div>

      <Alert type="success" onClose={() => setNotice("")}>{notice}</Alert>
      <Alert>{items.error || warehouses.error}</Alert>
      {noMasterData && (
        <Alert type="info">Add at least one item and one warehouse before recording stock.</Alert>
      )}

      <div className="panel">
        <StockInForm items={items.data || []} warehouses={warehouses.data || []} onSubmit={handleSubmit} />
      </div>

      <h2 className="section-title">Recent stock in</h2>
      <Alert>{history.error}</Alert>
      <Table columns={COLUMNS} rows={history.data} loading={history.loading} emptyMessage="No stock has been received yet." />
    </section>
  );
}
