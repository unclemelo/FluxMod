import { NavLink } from "react-router-dom";
import "../Styles/navbar.css";

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/info", label: "Info", end: true },
  { to: "/contributors", label: "Contributors", end: true },
];

export default function AppLayout({
  children,
  isAuthenticated,
  isAuthLoading,
  user,
  onLogin,
  onLogout,
}) {
  const username = user?.username || user?.id || "User";

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

          {isAuthenticated && (
            <NavLink
              to="/dashboard"
              end
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Dashboard
            </NavLink>
          )}

          <div className="login" id="auth-area">
            {isAuthLoading ? (
              <span className="user-info">Checking session...</span>
            ) : isAuthenticated ? (
              <>
                <span className="user-info">{username}</span>
                <button
                  type="button"
                  id="logout"
                  className="auth-btn logout-btn"
                  onClick={onLogout}
                >
                  Logout
                </button>
              </>
            ) : (
              <button
                type="button"
                id="login"
                className="auth-btn"
                onClick={onLogin}
              >
                Login
              </button>
            )}
          </div>
        </nav>
      </header>

      <main className="content">{children}</main>
    </div>
  );
}
