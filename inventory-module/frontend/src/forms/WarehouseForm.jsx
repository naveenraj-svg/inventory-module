import { useState } from "react";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Field from "../components/Field";
import { validateWarehouse } from "../utils/validation";

export default function WarehouseForm({ onSubmit, onCancel }) {
  const [values, setValues] = useState({ name: "", location: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const set = (field) => (e) => setValues((v) => ({ ...v, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const found = validateWarehouse(values);
    setErrors(found);
    if (Object.keys(found).length) return;

    setSaving(true);
    setFormError("");
    try {
      await onSubmit({ name: values.name.trim(), location: values.location.trim() || null });
    } catch (err) {
      setFormError(err.message);
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <Alert>{formError}</Alert>
      <div className="form-grid">
        <Field label="Warehouse name" value={values.name} onChange={set("name")} error={errors.name}
          placeholder="Fabric Store" maxLength={150} autoFocus />
        <Field label="Location" value={values.location} onChange={set("location")}
          placeholder="Block A, Coimbatore" maxLength={255} />
      </div>
      <div className="form-actions">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button type="submit" loading={saving}>Save warehouse</Button>
      </div>
    </form>
  );
}
