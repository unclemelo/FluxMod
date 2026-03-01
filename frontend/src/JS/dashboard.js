import { debugLog } from "./api.js";

export function renderGuilds(guilds) {
  debugLog("dashboard", "Rendering guild cards", { count: guilds?.length ?? 0 });
  const guildsContainer = document.getElementById("guilds");
  const guildSelect = document.getElementById("guild-select");
  const rawOutput = document.getElementById("raw");

  guildsContainer.innerHTML = "";
  guildSelect.innerHTML = "";

  for (const guild of guilds) {
    const guildCard = document.createElement("div");
    guildCard.className = "guild";
    guildCard.textContent = `${guild.name || guild.id} — ${guild.rule_count} rules`;
    guildsContainer.appendChild(guildCard);

    const option = document.createElement("option");
    option.value = guild.id;
    option.textContent = guild.name || guild.id;
    guildSelect.appendChild(option);
  }

  rawOutput.textContent = JSON.stringify(guilds, null, 2);
}

export function getRulePayloadFromForm() {
  const payload = {
    guildId: document.getElementById("guild-select").value,
    payload: {
      name: document.getElementById("rule-name").value,
      pattern: document.getElementById("rule-pattern").value,
      action: document.getElementById("rule-action").value,
      threshold: parseInt(document.getElementById("rule-threshold").value, 10) || 1,
      enabled: document.getElementById("rule-enabled").checked,
    },
  };

  debugLog("dashboard", "Built rule payload from form", payload);
  return payload;
}
