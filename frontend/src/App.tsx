import { useState } from "react";
import Dashboard from "./pages/GeneralDashboard";
import CustomerAnalysis from "./pages/CustomerAnalysis";

function App() {
  const [page, setPage] = useState<"dashboard" | "customer">("dashboard");

  return (
    <div>
      <nav>
        <button onClick={() => setPage("dashboard")}>
          Dashboard
        </button>

        <button onClick={() => setPage("customer")}>
          Customer Analysis
        </button>
      </nav>

      {/* Mounted only while visible, so it refetches fresh analytics each time
          (new customer analyses are saved to the database). */}
      {page === "dashboard" && <Dashboard />}

      {/* Always mounted, just hidden, so the form and results survive tab switches. */}
      <div style={{ display: page === "customer" ? "block" : "none" }}>
        <CustomerAnalysis />
      </div>
    </div>
  );
}

export default App;