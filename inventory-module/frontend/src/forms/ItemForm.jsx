import { useState } from "react";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Field from "../components/Field";
import { validateItem } from "../utils/validation";

const EMPTY = {
  code: "",
  name: "",
  category: "",
  uom: "",
  reorder_level: "0",
  unit_cost: "0",
};

export default function ItemForm({ onSubmit, onCancel }) {
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const set = (field) => (e) => setValues((v) => ({ ...v, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const found = validateItem(values);
    setErrors(found);
    if (Object.keys(found).length) return;

    setSaving(true);
    setFormError("");
    try {
      await onSubmit({
        code: values.code.trim(),
        name: values.name.trim(),
        category: values.category.trim() || null,
        uom: values.uom.trim(),
        reorder_level: values.reorder_level === "" ? 0 : Number(values.reorder_level),
        unit_cost: values.unit_cost === "" ? 0 : Number(values.unit_cost),
      });
    } catch (err) {
      setFormError(err.message);
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <Alert>{formError}</Alert>
      <div className="form-grid">
        <Field label="Item code" value={values.code} onChange={set("code")} error={errors.code}
          placeholder="FAB001" maxLength={50} autoFocus />
        <Field label="Item name" value={values.name} onChange={set("name")} error={errors.name}
          placeholder="Cotton fabric" maxLength={200} />
        <Field label="Category" value={values.category} onChange={set("category")} error={errors.category}
          placeholder="Fabric" maxLength={100} />
        <Field label="Unit of measure" value={values.uom} onChange={set("uom")} error={errors.uom}
          placeholder="KG, PCS, MTR" maxLength={20} />
        <Field label="Reorder level" type="number" min="0" step="any" inputMode="decimal"
          value={values.reorder_level} onChange={set("reorder_level")} error={errors.reorder_level}
          hint="Stock at or below this is flagged as low." />
        <Field label="Unit cost" type="number" min="0" step="any" inputMode="decimal"
          value={values.unit_cost} onChange={set("unit_cost")} error={errors.unit_cost} />
      </div>
      <div className="form-actions">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button type="submit" loading={saving}>Save item</Button>
      </div>
    </form>
  );
}
