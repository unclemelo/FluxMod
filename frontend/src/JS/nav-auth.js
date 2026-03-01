import { apiCall, debugLog, getBackendUrl } from "./api.js";
import { showLoggedIn, showLoggedOut } from "./auth.js";

const backendUrl = getBackendUrl();
debugLog("nav-auth", "Navigation auth module initialized", { backendUrl });

async function hydrateNavAuth() {
  debugLog("nav-auth", "Hydrating navbar auth state");
  try {
    const meResponse = await apiCall(backendUrl, "/api/me");

    if (meResponse.status === 401) {
      debugLog("nav-auth", "Navbar user is unauthenticated");
      showLoggedOut(backendUrl);
      return;
    }

    const user = await meResponse.json();
    debugLog("nav-auth", "Navbar user authenticated", {
      userId: user?.id,
      username: user?.username,
    });
    showLoggedIn(user, async () => {
      debugLog("nav-auth", "Navbar logout triggered");
      await apiCall(backendUrl, "/logout");
      window.location.reload();
    });
  } catch (error) {
    debugLog("nav-auth", "Failed to hydrate navbar auth", { error });
    console.error(error);
    showLoggedOut(backendUrl);
  }
}

hydrateNavAuth();
