const numberFormat = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 3 });
const moneyFormat = new Intl.NumberFormat("en-IN", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const formatNumber = (value) =>
  value === null || value === undefined ? "–" : numberFormat.format(value);

export const formatMoney = (value) =>
  value === null || value === undefined ? "–" : moneyFormat.format(value);

export const formatDate = (isoDate) => {
  if (!isoDate) return "–";
  const [y, m, d] = isoDate.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

export const todayISO = () => {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
};
