export function getBackendUrl() {
  // Priority: window.BACKEND_URL > localStorage > environment > sensible defaults
  const existing =
    (typeof window !== "undefined" && window.BACKEND_URL) ||
    localStorage.getItem("backendUrl");

  if (existing) {
    return existing;
  }

  // Auto-detect backend based on current environment
  let backendUrl = "http://localhost:8000"; // dev default

  if (typeof window !== "undefined" && window.location.hostname !== "localhost") {
    // In production on Render, backend is same origin
    // Use current origin (works whether frontend is on same service or different subdomain)
    backendUrl = window.location.origin.replace('fluxmod-frontend', 'fluxmod');
  }

  // Allow prompt override only in development
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    const promptUrl = prompt(
      "Enter backend URL (or press Cancel for http://localhost:8000):",
      backendUrl
    );
    if (promptUrl) {
      backendUrl = promptUrl;
    }
  }

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
