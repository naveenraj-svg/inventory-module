export default function Button({
  variant = "primary",
  type = "button",
  loading = false,
  disabled = false,
  children,
  ...rest
}) {
  return (
    <button
      type={type}
      className={`btn btn-${variant}`}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? "Working…" : children}
    </button>
  );
}
