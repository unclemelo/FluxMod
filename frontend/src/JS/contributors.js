import { debugLog } from "./api.js";

const owner = "unclemelo";
const repo = "FluxMod";
const container = document.querySelector('.grid-container');
const maintainers = ['unclemelo', 'hubot'];

async function loadContributors() {
  debugLog("contributors", "Loading contributors", { owner, repo });
  container.innerHTML = '';
  try {
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/contributors`);
    if (!res.ok) throw new Error(`Contributors fetch failed: ${res.status}`);
    const contributors = await res.json();
    debugLog("contributors", "Base contributor list loaded", {
      count: contributors?.length ?? 0,
    });

    // Fetch full profile for each contributor to get real name
    const profiles = await Promise.all(contributors.map(async c => {
      try {
        const r = await fetch(c.url);
        if (!r.ok) return { login: c.login, contributions: c.contributions, name: null, avatar_url: c.avatar_url };
        const profile = await r.json();
        return { login: c.login, contributions: c.contributions, name: profile.name || null, avatar_url: profile.avatar_url };
      } catch (e) {
        return { login: c.login, contributions: c.contributions, name: null, avatar_url: c.avatar_url };
      }
    }));

    // Render cards
    profiles.forEach(p => {
      const role = maintainers.includes(p.login) ? 'Maintainer' : 'Contributor';
      const card = document.createElement('div');
      card.className = 'contributor-card';
      card.innerHTML = `
        <div style="display:flex; align-items:center; gap:8px;">
          <img src="${p.avatar_url}" alt="${p.login}">
          <div>
            <div class="contributor-name">${p.name ? escapeHtml(p.name) : escapeHtml(p.login)}</div>
            <div class="contributor-role">${role}</div>
          </div>
        </div>
        <div style="margin-top:8px; color:var(--text-muted); font-size:0.85rem;">Commits: ${p.contributions}</div>
      `;
      container.appendChild(card);
    });

    debugLog("contributors", "Contributor cards rendered", {
      count: profiles?.length ?? 0,
    });

  } catch (err) {
    debugLog("contributors", "Failed to load contributors", { err });
    console.error('Error loading contributors:', err);
    container.innerHTML = '<div style="color:var(--text-muted);">Unable to load contributors. Check console for details.</div>';
  }
}

function escapeHtml(str){
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

loadContributors();