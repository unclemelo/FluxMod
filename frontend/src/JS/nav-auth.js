import { apiCall, getBackendUrl } from "./api.js";
import { showLoggedIn, showLoggedOut } from "./auth.js";

const backendUrl = getBackendUrl();

async function hydrateNavAuth() {
  try {
    const meResponse = await apiCall(backendUrl, "/api/me");

    if (meResponse.status === 401) {
      showLoggedOut(backendUrl);
      return;
    }

    const user = await meResponse.json();
    showLoggedIn(user, async () => {
      await apiCall(backendUrl, "/logout");
      window.location.reload();
    });
  } catch (error) {
    console.error(error);
    showLoggedOut(backendUrl);
  }
}

hydrateNavAuth();
