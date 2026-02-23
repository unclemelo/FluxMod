export function showLoggedOut(backendUrl) {
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  authArea.innerHTML = '<button id="login" class="auth-btn">Login</button>';
  document.getElementById("login").onclick = () => {
    window.location.href = `${backendUrl}/login`;
  };

  dashboardSection.style.display = "none";
}

export function showLoggedIn(user, onLogout) {
  const authArea = document.getElementById("auth-area");
  const dashboardSection = document.getElementById("dashboard");

  const username = user.username || user.id || "User";
  authArea.innerHTML = `<span class="user-info">${username}</span><button id="logout" class="auth-btn logout-btn">Logout</button>`;
  document.getElementById("logout").onclick = onLogout;

  dashboardSection.style.display = "block";
}
