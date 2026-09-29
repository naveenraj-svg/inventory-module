import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/items", label: "Items" },
  { to: "/warehouses", label: "Warehouses" },
  { to: "/stock-in", label: "Stock in" },
  { to: "/stock-out", label: "Stock out" },
  { to: "/current-stock", label: "Current stock" },
];

export default function Sidebar({ open, onNavigate }) {
  return (
    <aside className={`sidebar${open ? " open" : ""}`}>
      <div className="brand">
        <span className="brand-mark" aria-hidden="true" />
        Inventory module
      </div>
      <nav>
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            onClick={onNavigate}
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
