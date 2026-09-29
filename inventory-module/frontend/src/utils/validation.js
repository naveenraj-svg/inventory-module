const isBlank = (v) => v === undefined || v === null || String(v).trim() === "";

/** Returns a number for a numeric string, otherwise NaN. */
const toNumber = (v) => (isBlank(v) ? NaN : Number(v));

const decimalPlaces = (v) => {
  const [, decimals = ""] = String(v).trim().split(".");
  return decimals.length;
};

function checkNumber(errors, field, value, { label, min = 0, exclusiveMin = false, maxDecimals }) {
  const n = toNumber(value);
  if (Number.isNaN(n)) {
    errors[field] = `${label} must be a number.`;
  } else if (exclusiveMin ? n <= min : n < min) {
    errors[field] = exclusiveMin
      ? `${label} must be greater than ${min}.`
      : `${label} cannot be less than ${min}.`;
  } else if (maxDecimals !== undefined && decimalPlaces(value) > maxDecimals) {
    errors[field] = `${label} can have at most ${maxDecimals} decimal places.`;
  }
}

// NOTE: these checks are for quick feedback only. The backend validates everything again.

export function validateItem(v) {
  const errors = {};
  if (isBlank(v.code)) errors.code = "Item code is required.";
  if (isBlank(v.name)) errors.name = "Item name is required.";
  if (isBlank(v.uom)) errors.uom = "Unit of measure is required.";
  if (!isBlank(v.reorder_level))
    checkNumber(errors, "reorder_level", v.reorder_level, { label: "Reorder level", maxDecimals: 3 });
  if (!isBlank(v.unit_cost))
    checkNumber(errors, "unit_cost", v.unit_cost, { label: "Unit cost", maxDecimals: 2 });
  return errors;
}

export function validateWarehouse(v) {
  const errors = {};
  if (isBlank(v.name)) errors.name = "Warehouse name is required.";
  return errors;
}

function validateMovement(v) {
  const errors = {};
  if (isBlank(v.item_id)) errors.item_id = "Select an item.";
  if (isBlank(v.warehouse_id)) errors.warehouse_id = "Select a warehouse.";
  if (isBlank(v.quantity)) errors.quantity = "Quantity is required.";
  else
    checkNumber(errors, "quantity", v.quantity, {
      label: "Quantity",
      min: 0,
      exclusiveMin: true,
      maxDecimals: 3,
    });
  if (isBlank(v.transaction_date)) errors.transaction_date = "Date is required.";
  return errors;
}

export function validateStockIn(v) {
  const errors = validateMovement(v);
  if (!isBlank(v.unit_cost))
    checkNumber(errors, "unit_cost", v.unit_cost, { label: "Unit cost", maxDecimals: 2 });
  return errors;
}

export function validateStockOut(v, available) {
  const errors = validateMovement(v);
  if (!errors.quantity && available !== null && available !== undefined) {
    if (Number(v.quantity) > available) errors.quantity = "Insufficient stock.";
  }
  return errors;
}
