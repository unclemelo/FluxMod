import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";
import InfoPage from "./pages/InfoPage";
import ContributorsPage from "./pages/ContributorsPage";
import StatusPage from "./pages/status";
import { getBackendUrl } from "./JS/api";

function DashboardRoute({ isAuthLoading, isAuthenticated, user }) {
  if (isAuthLoading) {
    return (
      <section className="page-card">
        <p className="muted">Checking session...</p>
      </section>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <DashboardPage user={user} />;
}

export default function App() {
  const backendUrl = useMemo(() => getBackendUrl(), []);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [user, setUser] = useState(null);

  const hydrateAuth = useCallback(async () => {
    setIsAuthLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/me`, {
        credentials: "include",
      });

      if (response.status === 401) {
        setUser(null);
        return;
      }

      if (!response.ok) {
        throw new Error(`Auth check failed: ${response.status}`);
      }

      const currentUser = await response.json();
      setUser(currentUser);
    } catch (error) {
      console.error(error);
      setUser(null);
    } finally {
      setIsAuthLoading(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    hydrateAuth();
  }, [hydrateAuth]);

  const handleLogin = useCallback(() => {
    window.location.href = `${backendUrl}/login`;
  }, [backendUrl]);

  const handleLogout = useCallback(async () => {
    try {
      await fetch(`${backendUrl}/logout`, {
        credentials: "include",
      });
    } catch (error) {
      console.error(error);
    }

    setUser(null);
    window.location.href = "/";
  }, [backendUrl]);

  const isAuthenticated = Boolean(user);

  return (
    <AppLayout
      isAuthenticated={isAuthenticated}
      isAuthLoading={isAuthLoading}
      user={user}
      onLogin={handleLogin}
      onLogout={handleLogout}
    >
      <Routes>
        <Route
          path="/"
          element={
            <HomePage
              isAuthenticated={isAuthenticated}
              onLogin={handleLogin}
            />
          }
        />
        <Route
          path="/dashboard"
          element={
            <DashboardRoute
              isAuthLoading={isAuthLoading}
              isAuthenticated={isAuthenticated}
              user={user}
            />
          }
        />
        <Route path="/info" element={<InfoPage />} />
        <Route path="/contributors" element={<ContributorsPage />} />
        <Route path="/status" element={<StatusPage />} />
        <Route path="/status/:code" element={<StatusPage />} />
        <Route path="*" element={<Navigate to="/status?code=404" replace />} />
      </Routes>
    </AppLayout>
  );
}
