import { useState } from "react";
import Dashboard from "./pages/GeneralDashboard";
import CustomerAnalysis from "./pages/CustomerAnalysis";

function App() {
  const [page, setPage] = useState<"dashboard" | "customer">("dashboard");

  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-inner">
          <div className="navbar-brand">
            <span className="dot" />
            ChurnFlow
          </div>
          <div className="navbar-links">
            <button
              className={`nav-button ${page === "dashboard" ? "active" : ""}`}
              onClick={() => setPage("dashboard")}
            >
              Dashboard
            </button>
            <button
              className={`nav-button ${page === "customer" ? "active" : ""}`}
              onClick={() => setPage("customer")}
            >
              Customer Analysis
            </button>
          </div>
        </div>
      </nav>

      {/* Mounted only while visible, so it refetches fresh analytics each time
          (new customer analyses are saved to the database). */}
      {page === "dashboard" && <Dashboard />}

      {/* Always mounted, just hidden, so the form and results survive tab switches. */}
      <div className={page === "customer" ? "customer-view" : "is-hidden"}>
        <CustomerAnalysis />
      </div>
    </div>
  );
}

export default App;
