export default function Navbar({ onMenuClick }) {
  return (
    <header className="navbar">
      <button type="button" className="menu-btn" onClick={onMenuClick} aria-label="Open menu">
        <span />
        <span />
        <span />
      </button>
      <span className="navbar-title">Inventory</span>
    </header>
  );
}
