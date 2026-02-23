export function getBackendUrl() {
  const existingUrl =
    (typeof window !== "undefined" && window.BACKEND_URL) ||
    localStorage.getItem("backendUrl");

  const backendUrl =
    existingUrl ||
    prompt(
      "Enter backend URL (e.g. http://localhost:8000):",
      "http://localhost:8000"
    );

  if (backendUrl) {
    localStorage.setItem("backendUrl", backendUrl);
  }

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
