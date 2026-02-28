//import "../Styles/.css";
import React from "react"
import "../Styles/dashboard.css";
import "../Styles/defaults.css";


const User = "TestUser001"; // Placeholder username

export default function DashboardPage() {
  return (
    <section className="dashboard">
        <div className="Sidebar">
            <h1>Dashboard</h1>
            <nav>
                <ul>
                    <img className="sidebar-profile-picture" src="{userProfilePicture}" alt="{User}" />
                    <h2 className="sidebar-welcome-header">Welcome, {User}</h2>

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