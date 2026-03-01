import { debugLog } from "./api.js";

function setDashboardNavVisibility(isVisible) {
  debugLog("auth", "Setting dashboard nav visibility", { isVisible });
  const dashboardLinks = document.querySelectorAll(".nav-dashboard");
  for (const link of dashboardLinks) {
    link.style.display = isVisible ? "inline-block" : "none";
  }
}

export function showLoggedOut(backendUrl) {
  debugLog("auth", "Rendering logged-out state", { backendUrl });
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  setDashboardNavVisibility(false);

  authArea.innerHTML = '<button id="login" class="auth-btn">Login</button>';
  document.getElementById("login").onclick = () => {
    debugLog("auth", "Login button clicked", { redirectTo: `${backendUrl}/login` });
    window.location.href = `${backendUrl}/login`;
  };

  if (dashboardSection) {
    dashboardSection.style.display = "none";
  }
}

export function showLoggedIn(user, onLogout) {
  debugLog("auth", "Rendering logged-in state", {
    userId: user?.id,
    username: user?.username,
  });
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  setDashboardNavVisibility(true);

  const username = user.username || user.id || "User";
  authArea.innerHTML = `<span class="user-info">${user}</span><button id="logout" class="auth-btn logout-btn">Logout</button>`;
  document.getElementById("logout").onclick = () => {
    debugLog("auth", "Logout button clicked");
    onLogout();
  };

  if (dashboardSection) {
    dashboardSection.style.display = "block";
  }
}
