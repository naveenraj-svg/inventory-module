/**
 * columns: [{ key, header, align?: "right", render?: (row) => node }]
 * rowClassName: optional (row) => string
 */
export default function Table({
  columns,
  rows,
  rowKey = "id",
  loading = false,
  emptyMessage = "Nothing here yet.",
  rowClassName,
}) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} className={c.align === "right" ? "num" : undefined}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading && !rows?.length ? (
            <tr>
              <td colSpan={columns.length} className="table-empty">
                Loading…
              </td>
            </tr>
          ) : !rows?.length ? (
            <tr>
              <td colSpan={columns.length} className="table-empty">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={typeof rowKey === "function" ? rowKey(row) : row[rowKey]} className={rowClassName?.(row)}>
                {columns.map((c) => (
                  <td key={c.key} className={c.align === "right" ? "num" : undefined}>
                    {c.render ? c.render(row) : row[c.key] ?? "–"}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
