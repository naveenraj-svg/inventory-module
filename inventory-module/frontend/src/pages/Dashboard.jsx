import { Link } from "react-router-dom";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Table from "../components/Table";
import useApi from "../hooks/useApi";
import { getCurrentStock, getSummary, getTransactions } from "../services/api";
import { formatDate, formatNumber } from "../utils/format";
import { STOCK_COLUMNS, stockRowClass, stockRowKey } from "./CurrentStock";

const TX_COLUMNS = [
  { key: "transaction_date", header: "Date", render: (r) => formatDate(r.transaction_date) },
  { key: "transaction_type", header: "Type", render: (r) => <Badge value={r.transaction_type} /> },
  { key: "item", header: "Item", render: (r) => `${r.item_code} – ${r.item_name}` },
  { key: "warehouse_name", header: "Warehouse" },
  { key: "quantity", header: "Quantity", align: "right", render: (r) => `${formatNumber(r.quantity)} ${r.uom}` },
];

export default function Dashboard() {
  const summary = useApi(getSummary, []);
  const low = useApi(getCurrentStock, [{ low_only: true }]);
  const recent = useApi(getTransactions, [{ limit: 8 }]);
  const s = summary.data;

  const stats = [
    { label: "Items", value: s?.total_items },
    { label: "Warehouses", value: s?.total_warehouses },
    { label: "Low stock lines", value: s?.low_stock_count, alert: s?.low_stock_count > 0 },
    { label: "Transactions", value: s?.total_transactions },
  ];

  return (
    <section className="dashboard-page">
      <div className="dashboard-hero">
        <div className="dashboard-copy">
          <p className="eyebrow">Inventory / Overview</p>
          <h1>Dashboard</h1>
          <p className="page-sub">Where stock stands today.</p>
        </div>
        <div className="material-art" aria-hidden="true">
          <div className="material-art-label">MATERIAL FLOW</div>
          <div className="fabric-roll roll-sage"><span /></div>
          <div className="fabric-roll roll-ochre"><span /></div>
          <div className="fabric-roll roll-coral"><span /></div>
          <div className="fabric-roll roll-blue"><span /></div>
          <div className="art-stitch" />
        </div>
      </div>

      <Alert>{summary.error || low.error || recent.error}</Alert>

      <dl className="stats dashboard-stats">
        {stats.map((st) => (
          <div key={st.label} className={`stat${st.alert ? " stat-alert" : ""}`}>
            <dt>{st.label}</dt>
            <dd>{st.value === undefined ? "–" : formatNumber(st.value)}</dd>
          </div>
        ))}
      </dl>

      <div className="section-row">
        <h2 className="section-title">Low stock</h2>
        <Link to="/current-stock">View all stock</Link>
      </div>
      <Table
        columns={STOCK_COLUMNS}
        rows={low.data}
        rowKey={stockRowKey}
        rowClassName={stockRowClass}
        loading={low.loading}
        emptyMessage="Nothing is running low."
      />

      <h2 className="section-title">Recent transactions</h2>
      <Table columns={TX_COLUMNS} rows={recent.data} loading={recent.loading} emptyMessage="No transactions yet." />
    </section>
  );
}
