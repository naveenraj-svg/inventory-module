import { useState } from "react";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Field from "../components/Field";
import { todayISO } from "../utils/format";
import { validateStockIn } from "../utils/validation";

const emptyValues = () => ({
  item_id: "",
  warehouse_id: "",
  quantity: "",
  unit_cost: "",
  supplier: "",
  transaction_date: todayISO(),
  remarks: "",
});

export default function StockInForm({ items, warehouses, onSubmit }) {
  const [values, setValues] = useState(emptyValues);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const set = (field) => (e) => setValues((v) => ({ ...v, [field]: e.target.value }));
  const selectedItem = items.find((i) => String(i.id) === values.item_id);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const found = validateStockIn(values);
    setErrors(found);
    if (Object.keys(found).length) return;

    setSaving(true);
    setFormError("");
    try {
      await onSubmit({
        item_id: Number(values.item_id),
        warehouse_id: Number(values.warehouse_id),
        quantity: Number(values.quantity),
        unit_cost: values.unit_cost === "" ? null : Number(values.unit_cost),
        supplier: values.supplier.trim() || null,
        transaction_date: values.transaction_date,
        remarks: values.remarks.trim() || null,
      });
      // keep the chosen warehouse to speed up repeated entries
      setValues((v) => ({ ...emptyValues(), warehouse_id: v.warehouse_id }));
    } catch (err) {
      setFormError(err.message);
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
        <Field label={`Quantity${selectedItem ? ` (${selectedItem.uom})` : ""}`} type="number" min="0" step="any"
          inputMode="decimal" value={values.quantity} onChange={set("quantity")} error={errors.quantity} />
        <Field label="Unit of measure" value={selectedItem?.uom || ""} readOnly disabled
          hint="Comes from the item master." />
        <Field label="Unit cost" type="number" min="0" step="any" inputMode="decimal"
          value={values.unit_cost} onChange={set("unit_cost")} error={errors.unit_cost}
          placeholder={selectedItem ? String(selectedItem.unit_cost) : ""}
          hint="Leave blank to use the item's standard cost." />
        <Field label="Supplier" value={values.supplier} onChange={set("supplier")} maxLength={200} />
        <Field label="Date" type="date" value={values.transaction_date} onChange={set("transaction_date")}
          error={errors.transaction_date} />
        <Field as="textarea" rows={2} label="Remarks" value={values.remarks} onChange={set("remarks")} maxLength={1000} />
      </div>
      <div className="form-actions">
        <Button type="submit" loading={saving}>Record stock in</Button>
      </div>
    </form>
  );
}
