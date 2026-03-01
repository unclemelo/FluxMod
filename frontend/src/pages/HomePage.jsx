import "../Styles/defaults.css";
import "../Styles/landing.css"
import FluxModLogo from "./static-imgs/fluxmod.png";

export default function HomePage({ isAuthenticated, onLogin }) {
  return (
    <>
      <section className="title-card">
          <img className="fluxmod-logo" src={FluxModLogo} alt="FluxMod Logo" />
          <h1>FluxMod / Dashboard</h1>
          <p className="title-desc">Your all-in-one AutoMod solution for Fluxer guilds.</p>
          <button
            type="button"
            className="login-w-fluxer"
            id="login"
            onClick={onLogin}
          >
            <i className="fa-solid fa-arrow-right-to-bracket"></i>{" "}
            {isAuthenticated ? "Switch Account" : "Login with Fluxer"}
          </button>
      </section>

      {/* <section className="stat-card hero-stat">
          <div className="stat-content">
            <span className="stat-label">Protected Servers</span>
            <span className="stat-value" id="protected-guilds-count">—</span>
          </div>
      </section> */}
    </>
  );
}
