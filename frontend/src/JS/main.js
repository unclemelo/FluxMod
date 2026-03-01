import { apiCall, debugLog, getBackendUrl } from "./api.js";
import { showLoggedIn } from "./auth.js";
import { getRulePayloadFromForm, renderGuilds } from "./dashboard.js";

const backendUrl = getBackendUrl();
debugLog("main", "Main dashboard module initialized", { backendUrl });

async function checkAuth() {
  debugLog("main", "Starting checkAuth");
  const statusSection = document.getElementById("status");

  try {
    const meResponse = await apiCall(backendUrl, "/api/me");

    if (meResponse.status === 401) {
      window.location.href = "./index.html";
      return;
    }

    const user = await meResponse.json();
    debugLog("main", "User profile loaded", {
      userId: user?.id,
      username: user?.username,
    });
    const guildsResponse = await apiCall(backendUrl, "/api/guilds");
    const guilds = await guildsResponse.json();
    debugLog("main", "Guild list loaded", { count: guilds?.length ?? 0 });

    showLoggedIn(user, async () => {
      debugLog("main", "Processing logout from dashboard");
      await apiCall(backendUrl, "/logout");
      window.location.href = "./index.html";
    });

    renderGuilds(guilds);
    statusSection.innerHTML = "";
  } catch (error) {
    debugLog("main", "checkAuth failed", { error });
    statusSection.innerHTML = `<p class="muted">Error: ${error.message}</p>`;
    console.error(error);
  }
}

async function handleCreateRuleSubmit(event) {
  debugLog("main", "Rule create form submitted");
  event.preventDefault();

  const { guildId, payload } = getRulePayloadFromForm();
  debugLog("main", "Collected rule payload", { guildId, payload });

  try {
    const response = await apiCall(
      backendUrl,
      `/api/guilds/${encodeURIComponent(guildId)}/rules`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );

    if (response.status === 201) {
      debugLog("main", "Rule created successfully", { guildId });
      alert("Rule created");
      await checkAuth();
      return;
    }

    if (response.status === 401) {
      alert("Not authorized — login required");
      return;
    }

    const errorText = await response.text();
    alert(`Error: ${response.status} ${errorText}`);
  } catch (error) {
    debugLog("main", "Rule creation failed", { error });
    alert(`Request failed: ${error.message}`);
  }
}

document
  .getElementById("create-rule-form")
  .addEventListener("submit", handleCreateRuleSubmit);

debugLog("main", "Running initial checkAuth");
checkAuth();
