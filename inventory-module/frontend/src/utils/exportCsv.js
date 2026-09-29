import { downloadCurrentStockCsv } from "../services/api";

/** Downloads the current-stock CSV (with the same filters as the table). */
export async function exportCurrentStockCsv(filters) {
  const { blob, filename } = await downloadCurrentStockCsv(filters);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
