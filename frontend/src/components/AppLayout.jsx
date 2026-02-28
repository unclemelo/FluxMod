import { NavLink } from "react-router-dom";
import "../Styles/navbar.css";

const links = [
  { to: "/", label: "Home", end: true },
  // { to: "/dashboard", label: "Dashboard", end: true },
  { to: "/info", label: "Info", end: true },
  { to: "/contributors", label: "Contributors", end: true },
];

export default function AppLayout({ children }) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <NavLink className="brand" to="/" end>
          FluxMod
        </NavLink>

        <nav className="nav-links" aria-label="Main navigation">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {link.label}
            </NavLink>
          ))}

          <div className="login" id="auth-area"></div>
        </nav>
      </header>

      <main className="content">{children}</main>
    </div>
  );
}
