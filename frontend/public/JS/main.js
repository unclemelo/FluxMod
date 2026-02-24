import { apiCall, getBackendUrl } from "./api.js";
import { showLoggedIn } from "./auth.js";
import { getRulePayloadFromForm, renderGuilds } from "./dashboard.js";

const backendUrl = getBackendUrl();

async function checkAuth() {
  const statusSection = document.getElementById("status");

  try {
    const meResponse = await apiCall(backendUrl, "/api/me");

    if (meResponse.status === 401) {
      window.location.href = "./index.html";
      return;
    }

    const user = await meResponse.json();
    const guildsResponse = await apiCall(backendUrl, "/api/guilds");
    const guilds = await guildsResponse.json();

    showLoggedIn(user, async () => {
      await apiCall(backendUrl, "/logout");
      window.location.href = "./index.html";
    });

    renderGuilds(guilds);
    statusSection.innerHTML = "";
  } catch (error) {
    statusSection.innerHTML = `<p class="muted">Error: ${error.message}</p>`;
    console.error(error);
  }
}

async function handleCreateRuleSubmit(event) {
  event.preventDefault();

  const { guildId, payload } = getRulePayloadFromForm();

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
    alert(`Request failed: ${error.message}`);
  }
}

document
  .getElementById("create-rule-form")
  .addEventListener("submit", handleCreateRuleSubmit);

checkAuth();
