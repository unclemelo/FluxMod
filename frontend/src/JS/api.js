function isLocalHost(hostname) {
  return hostname === "localhost" || hostname === "127.0.0.1";
}

function normalizeBackendUrl(url) {
  if (!url || typeof url !== "string") {
    return null;
  }

  const trimmed = url.trim().replace(/\/$/, "");
  if (!trimmed) {
    return null;
  }

  try {
    return new URL(trimmed).toString().replace(/\/$/, "");
  } catch {
    return null;
  }
}

function resolveProductionBackend(origin) {
  if (!origin) {
    return null;
  }

  if (origin.includes("fluxmod-frontend.onrender.com")) {
    return origin.replace("fluxmod-frontend", "fluxmod");
  }

  return origin;
}

function isOnStatusPage() {
  if (typeof window === "undefined") {
    return false;
  }

  return window.location.pathname.startsWith("/status");
}

export function redirectToStatus(code) {
  if (typeof window === "undefined") {
    return;
  }

  const normalized = Number.parseInt(code, 10);
  const safeCode =
    Number.isInteger(normalized) && normalized >= 100 && normalized <= 599
      ? normalized
      : 500;

  if (isOnStatusPage()) {
    return;
  }

  window.location.assign(`/status?code=${safeCode}`);
}

export function getBackendUrl() {
  // Priority: window.BACKEND_URL > scoped localStorage > legacy localStorage > environment defaults
  if (typeof window === "undefined") {
    return "http://localhost:8000";
  }

  const { origin, hostname, protocol } = window.location;
  const storageKey = `backendUrl:${origin}`;

  const configured = normalizeBackendUrl(window.BACKEND_URL);
  if (configured) {
    localStorage.setItem(storageKey, configured);
    localStorage.setItem("backendUrl", configured);
    return configured;
  }

  const scopedSaved = normalizeBackendUrl(localStorage.getItem(storageKey));
  const legacySaved = normalizeBackendUrl(localStorage.getItem("backendUrl"));
  const existing = scopedSaved || legacySaved;

  if (existing) {
    const parsed = new URL(existing);
    const isProdPage = !isLocalHost(hostname);
    const invalidForProd =
      isProdPage &&
      (isLocalHost(parsed.hostname) ||
        (protocol === "https:" && parsed.protocol !== "https:"));

    if (!invalidForProd) {
      localStorage.setItem(storageKey, existing);
      return existing;
    }

    localStorage.removeItem("backendUrl");
    localStorage.removeItem(storageKey);
  }

  let backendUrl = "http://localhost:8000";

  if (!isLocalHost(hostname)) {
    backendUrl = resolveProductionBackend(origin) || origin;
  }

  if (isLocalHost(hostname)) {
    const promptUrl = prompt(
      "Enter backend URL (or press Cancel for http://localhost:8000):",
      backendUrl
    );
    const prompted = normalizeBackendUrl(promptUrl);
    if (prompted) {
      backendUrl = prompted;
    }
  }

  localStorage.setItem(storageKey, backendUrl);
  localStorage.setItem("backendUrl", backendUrl);
  return backendUrl;
}

export async function apiCall(backendUrl, path, options = {}) {
  let response;

  try {
    response = await fetch(`${backendUrl}${path}`, {
      credentials: "include",
      ...options,
    });
  } catch (error) {
    redirectToStatus(503);
    throw error;
  }

  if (!response.ok) {
    redirectToStatus(response.status);
    const errorText = await response.text();
    throw new Error(`${response.status}: ${errorText}`);
  }

  return response;
}
