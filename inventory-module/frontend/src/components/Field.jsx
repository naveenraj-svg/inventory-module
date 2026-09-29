import { useId } from "react";

/** A label + input/select/textarea with an inline error message. */
export default function Field({ label, error, hint, as = "input", children, ...props }) {
  const id = useId();
  const Tag = as;
  return (
    <div className={`field${error ? " field-error" : ""}`}>
      <label htmlFor={id}>{label}</label>
      <Tag id={id} aria-invalid={Boolean(error)} aria-describedby={`${id}-msg`} {...props}>
        {children}
      </Tag>
      <p id={`${id}-msg`} className={error ? "field-msg error" : "field-msg"}>
        {error || hint || ""}
      </p>
    </div>
  );
}
