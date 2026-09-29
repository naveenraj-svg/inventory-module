import { useState } from "react";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Modal from "../components/Modal";
import Table from "../components/Table";
import WarehouseForm from "../forms/WarehouseForm";
import useApi from "../hooks/useApi";
import { createWarehouse, getWarehouses } from "../services/api";

const COLUMNS = [
  { key: "name", header: "Warehouse", render: (r) => <strong>{r.name}</strong> },
  { key: "location", header: "Location" },
  { key: "is_active", header: "Status", render: (r) => <Badge value={r.is_active ? "Active" : "Inactive"} /> },
];

export default function Warehouses() {
  const [showForm, setShowForm] = useState(false);
  const [notice, setNotice] = useState("");
  const { data, loading, error, reload } = useApi(getWarehouses, []);

  const handleCreate = async (payload) => {
    const warehouse = await createWarehouse(payload);
    setShowForm(false);
    setNotice(`Warehouse “${warehouse.name}” was added.`);
    reload();
  };

  return (
    <section>
      <div className="page-head">
        <div>
          <h1>Warehouses</h1>
          <p className="page-sub">Places where stock is kept.</p>
        </div>
        <Button onClick={() => setShowForm(true)}>Add warehouse</Button>
      </div>

      <Alert type="success" onClose={() => setNotice("")}>{notice}</Alert>
      <Alert>{error}</Alert>

      <Table
        columns={COLUMNS}
        rows={data}
        loading={loading}
        emptyMessage="No warehouses yet. Use “Add warehouse” to create one."
      />

      {showForm && (
        <Modal title="Add warehouse" onClose={() => setShowForm(false)}>
          <WarehouseForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
        </Modal>
      )}
    </section>
  );
}
