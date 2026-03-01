//import "../Styles/.css";
import React from "react"
import "../Styles/dashboard.css";
import "../Styles/defaults.css";

export default function DashboardPage({ user }) {
  const username = user?.username || user?.id || "User";

  return (
    <section className="dashboard">
        <div className="Sidebar">
            <h1>Dashboard</h1>
            <nav>
                <ul>
                    <h2 className="sidebar-welcome-header">Welcome, {username}</h2>

                    <h2 className="sidebar-title">General</h2>
                    <li><a href="/dashboard/servers"><i className="fa-solid fa-server"></i> Servers</a></li>
                    <li><a href="/dashboard/settings"><i className="fa-solid fa-gear"></i> Settings</a></li>
                    <h2 className="sidebar-title">Management</h2>
                    <li><a href="/dashboard/logs"><i className="fa-solid fa-file-alt"></i> Logs</a></li>
                    <li><a href="/dashboard/analytics"><i className="fa-solid fa-chart-line"></i> Analytics</a></li>
                </ul>
            </nav>
        </div>
        <div className="MainContent">
            
        </div>
    </section>
  );
} 