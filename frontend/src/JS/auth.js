function setDashboardNavVisibility(isVisible) {
  const dashboardLinks = document.querySelectorAll(".nav-dashboard");
  for (const link of dashboardLinks) {
    link.style.display = isVisible ? "inline-block" : "none";
  }
}

export function showLoggedOut(backendUrl) {
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  setDashboardNavVisibility(false);

  authArea.innerHTML = '<button id="login" class="auth-btn">Login</button>';
  document.getElementById("login").onclick = () => {
    window.location.href = `${backendUrl}/login`;
  };

  if (dashboardSection) {
    dashboardSection.style.display = "none";
  }
}

export function showLoggedIn(user, onLogout) {
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  setDashboardNavVisibility(true);
  console.log("User authenticated:", user);

  const username = user.username || user.id || "User";
  authArea.innerHTML = `<span class="user-info">${user}</span><button id="logout" class="auth-btn logout-btn">Logout</button>`;
  document.getElementById("logout").onclick = onLogout;

  if (dashboardSection) {
    dashboardSection.style.display = "block";
  }
}
