import { useEffect, useState } from "react";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Field from "../components/Field";
import { getAvailableStock } from "../services/api";
import { formatNumber, todayISO } from "../utils/format";
import { validateStockOut } from "../utils/validation";

const emptyValues = () => ({
  item_id: "",
  warehouse_id: "",
  quantity: "",
  transaction_date: todayISO(),
  remarks: "",
});

export default function StockOutForm({ items, warehouses, onSubmit }) {
  const [values, setValues] = useState(emptyValues);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);
  const [available, setAvailable] = useState(null); // { available, uom } | null
  const [availableError, setAvailableError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const set = (field) => (e) => setValues((v) => ({ ...v, [field]: e.target.value }));

  // Look up the available stock whenever the item / warehouse changes
  useEffect(() => {
    setAvailable(null);
    setAvailableError("");
    if (!values.item_id || !values.warehouse_id) return undefined;

    let cancelled = false;
    getAvailableStock({ item_id: values.item_id, warehouse_id: values.warehouse_id })
      .then((res) => !cancelled && setAvailable(res))
      .catch((err) => !cancelled && setAvailableError(err.message));
    return () => {
      cancelled = true;
    };
  }, [values.item_id, values.warehouse_id, refreshKey]);

  const availableQty = available ? available.available : null;
  const overdrawn =
    availableQty !== null && values.quantity !== "" && Number(values.quantity) > availableQty;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const found = validateStockOut(values, availableQty);
    setErrors(found);
    if (Object.keys(found).length) return;

    setSaving(true);
    setFormError("");
    try {
      await onSubmit({
        item_id: Number(values.item_id),
        warehouse_id: Number(values.warehouse_id),
        quantity: Number(values.quantity),
        transaction_date: values.transaction_date,
        remarks: values.remarks.trim() || null,
      });
      setValues((v) => ({ ...emptyValues(), item_id: v.item_id, warehouse_id: v.warehouse_id }));
      setRefreshKey((k) => k + 1);
    } catch (err) {
      // The server is the source of truth (e.g. someone else took stock meanwhile)
      setFormError(err.message);
      setRefreshKey((k) => k + 1);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <Alert>{formError}</Alert>
      <div className="form-grid">
        <Field as="select" label="Item" value={values.item_id} onChange={set("item_id")} error={errors.item_id}>
          <option value="">Select an item</option>
          {items.map((i) => (
            <option key={i.id} value={i.id}>{i.code} – {i.name}</option>
          ))}
        </Field>
        <Field as="select" label="Warehouse" value={values.warehouse_id} onChange={set("warehouse_id")} error={errors.warehouse_id}>
          <option value="">Select a warehouse</option>
          {warehouses.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </Field>

        <div className="available" aria-live="polite">
          <span className="available-label">Available stock</span>
          <span className={`available-value${availableQty === 0 ? " zero" : ""}`}>
            {availableError
              ? "Could not load"
              : available
              ? `${formatNumber(available.available)} ${available.uom}`
              : "Select an item and warehouse"}
          </span>
        </div>

        <Field label="Quantity" type="number" min="0" step="any" inputMode="decimal"
          value={values.quantity} onChange={set("quantity")}
          error={errors.quantity || (overdrawn ? "Insufficient stock." : "")} />
        <Field label="Date" type="date" value={values.transaction_date} onChange={set("transaction_date")}
          error={errors.transaction_date} />
        <Field as="textarea" rows={2} label="Remarks" value={values.remarks} onChange={set("remarks")} maxLength={1000} />
      </div>
      <div className="form-actions">
        <Button type="submit" loading={saving} disabled={overdrawn}>Record stock out</Button>
      </div>
    </form>
  );
}
