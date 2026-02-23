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
    // In production (e.g., Netlify), assume backend is on Render at standard URL
    backendUrl = "https://fluxmod.onrender.comm";
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
