import { useEffect, useState } from "react";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Modal from "../components/Modal";
import Table from "../components/Table";
import ItemForm from "../forms/ItemForm";
import useApi from "../hooks/useApi";
import { createItem, getItems } from "../services/api";
import { formatMoney, formatNumber } from "../utils/format";

const COLUMNS = [
  { key: "code", header: "Code", render: (r) => <strong>{r.code}</strong> },
  { key: "name", header: "Name" },
  { key: "category", header: "Category" },
  { key: "uom", header: "UOM" },
  { key: "reorder_level", header: "Reorder level", align: "right", render: (r) => formatNumber(r.reorder_level) },
  { key: "unit_cost", header: "Unit cost", align: "right", render: (r) => formatMoney(r.unit_cost) },
  { key: "is_active", header: "Status", render: (r) => <Badge value={r.is_active ? "Active" : "Inactive"} /> },
];

export default function Items() {
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [notice, setNotice] = useState("");

  // debounce the search box
  useEffect(() => {
    const t = setTimeout(() => setQuery(search.trim()), 250);
    return () => clearTimeout(t);
  }, [search]);

  const { data, loading, error, reload } = useApi(getItems, [{ q: query }]);

  const handleCreate = async (payload) => {
    const item = await createItem(payload);
    setShowForm(false);
    setNotice(`Item ${item.code} was added.`);
    reload();
  };

  return (
    <section>
      <div className="page-head">
        <div>
          <h1>Items</h1>
          <p className="page-sub">The item master. Every stock movement refers to an item here.</p>
        </div>
        <Button onClick={() => setShowForm(true)}>Add item</Button>
      </div>

      <Alert type="success" onClose={() => setNotice("")}>{notice}</Alert>
      <Alert>{error}</Alert>

      <div className="toolbar">
        <input
          type="search"
          className="input"
          placeholder="Search by code or name"
          aria-label="Search items"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Table
        columns={COLUMNS}
        rows={data}
        loading={loading}
        emptyMessage={query ? "No items match your search." : "No items yet. Use “Add item” to create the first one."}
      />

      {showForm && (
        <Modal title="Add item" onClose={() => setShowForm(false)}>
          <ItemForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
        </Modal>
      )}
    </section>
  );
}
