export function showLoggedOut(backendUrl) {
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  authArea.innerHTML = '<button id="login">Login</button>';
  document.getElementById("login").onclick = () => {
    window.location.href = `${backendUrl}/login`;
  };

  dashboardSection.style.display = "none";
}

export function showLoggedIn(onLogout) {
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  authArea.innerHTML = '<button id="logout">Logout</button>';
  document.getElementById("logout").onclick = onLogout;

  dashboardSection.style.display = "block";
}
