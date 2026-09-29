const BASE_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(
  /\/$/,
  ""
);

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** FastAPI returns either a string or a list of validation problems. */
function formatDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc)
          ? d.loc.filter((p) => p !== "body" && p !== "query").join(".")
          : "";
        return field ? `${field}: ${d.msg}` : d.msg;
      })
      .join("; ");
  }
  return "Something went wrong. Please try again.";
}

function buildQuery(params = {}) {
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "" || value === false) return;
    sp.append(key, String(value));
  });
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

async function send(path, { method = "GET", body, params } = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}${buildQuery(params)}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(
      "Cannot reach the server. Check that the backend is running.",
      0
    );
  }

  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const data = await response.json();
      message = formatDetail(data.detail);
    } catch {
      /* body was not JSON */
    }
    throw new ApiError(message, response.status);
  }
  return response;
}

async function request(path, options) {
  const response = await send(path, options);
  return response.json();
}

// ---- Items ---------------------------------------------------------------
export const getItems = (params) => request("/items", { params });
export const createItem = (body) => request("/items", { method: "POST", body });

// ---- Warehouses ----------------------------------------------------------
export const getWarehouses = (params) => request("/warehouses", { params });
export const createWarehouse = (body) =>
  request("/warehouses", { method: "POST", body });

// ---- Stock ---------------------------------------------------------------
export const stockIn = (body) => request("/stock-in", { method: "POST", body });
export const stockOut = (body) => request("/stock-out", { method: "POST", body });
export const getCurrentStock = (params) => request("/stock/current", { params });
export const getAvailableStock = (params) => request("/stock/available", { params });
export const getTransactions = (params) => request("/stock/transactions", { params });
export const getSummary = () => request("/stock/summary");

export async function downloadCurrentStockCsv(params) {
  const response = await send("/stock/current/export", { params });
  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  return { blob, filename: match ? match[1] : "current-stock.csv" };
}
