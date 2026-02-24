import { apiCall, getBackendUrl } from "./api.js";
import { showLoggedOut } from "./auth.js";

const backendUrl = getBackendUrl();

async function renderProtectedGuilds() {
  const countElement = document.getElementById("protected-guilds-count");
  if (!countElement) {
    return;
  }

  try {
    const response = await apiCall(backendUrl, "/api/public/stats");
    const stats = await response.json();
    const count = Number.isFinite(stats?.protected_guilds)
      ? stats.protected_guilds
      : 0;
    countElement.textContent = String(count);
  } catch (error) {
    countElement.textContent = "0";
    console.error(error);
  }
}

async function checkLandingAuth() {
  const statusSection = document.getElementById("status");

  try {
    const meResponse = await apiCall(backendUrl, "/api/me");

    if (meResponse.status === 401) {
      showLoggedOut(backendUrl);
      statusSection.innerHTML =
        '<p class="muted">Not signed in — click login to continue.</p>';
      return;
    }

    window.location.href = "./dashboard.html";
  } catch (error) {
    showLoggedOut(backendUrl);
    statusSection.innerHTML = `<p class="muted">Error: ${error.message}</p>`;
    console.error(error);
  }
}

checkLandingAuth();
renderProtectedGuilds();