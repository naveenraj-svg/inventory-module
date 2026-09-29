import { useState } from "react";
import Alert from "../components/Alert";
import Table from "../components/Table";
import StockOutForm from "../forms/StockOutForm";
import useApi from "../hooks/useApi";
import { getItems, getTransactions, getWarehouses, stockOut } from "../services/api";
import { formatDate, formatNumber } from "../utils/format";

const COLUMNS = [
  { key: "transaction_date", header: "Date", render: (r) => formatDate(r.transaction_date) },
  { key: "item", header: "Item", render: (r) => `${r.item_code} – ${r.item_name}` },
  { key: "warehouse_name", header: "Warehouse" },
  { key: "quantity", header: "Quantity", align: "right", render: (r) => `${formatNumber(r.quantity)} ${r.uom}` },
  { key: "remarks", header: "Remarks" },
];

export default function StockOut() {
  const [notice, setNotice] = useState("");
  const items = useApi(getItems, [{ active_only: true, limit: 500 }]);
  const warehouses = useApi(getWarehouses, [{ active_only: true }]);
  const history = useApi(getTransactions, [{ transaction_type: "OUT", limit: 10 }]);

  const handleSubmit = async (payload) => {
    const tx = await stockOut(payload);
    setNotice(`Issued ${formatNumber(tx.quantity)} ${tx.uom} of ${tx.item_code} from ${tx.warehouse_name}.`);
    history.reload();
  };

  return (
    <section>
      <div className="page-head">
        <div>
          <h1>Stock out</h1>
          <p className="page-sub">Issue goods from a warehouse. You cannot issue more than what is available.</p>
        </div>
      </div>

      <Alert type="success" onClose={() => setNotice("")}>{notice}</Alert>
      <Alert>{items.error || warehouses.error}</Alert>

      <div className="panel">
        <StockOutForm items={items.data || []} warehouses={warehouses.data || []} onSubmit={handleSubmit} />
      </div>

      <h2 className="section-title">Recent stock out</h2>
      <Alert>{history.error}</Alert>
      <Table columns={COLUMNS} rows={history.data} loading={history.loading} emptyMessage="No stock has been issued yet." />
    </section>
  );
}
