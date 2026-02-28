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
  const response = await fetch(`${backendUrl}${path}`, {
    credentials: "include",
    ...options,
  });

  if (!response.ok && response.status !== 401) {
    const errorText = await response.text();
    throw new Error(`${response.status}: ${errorText}`);
  }

  return response;
}
