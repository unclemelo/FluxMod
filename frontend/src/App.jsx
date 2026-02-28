import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";
import InfoPage from "./pages/InfoPage";
import ContributorsPage from "./pages/ContributorsPage";
import StatusPage from "./pages/status";

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/info" element={<InfoPage />} />
        <Route path="/contributors" element={<ContributorsPage />} />
        <Route path="/status" element={<StatusPage />} />
        <Route path="/status/:code" element={<StatusPage />} />
        <Route path="*" element={<Navigate to="/status?code=404" replace />} />
      </Routes>
    </AppLayout>
  );
}
