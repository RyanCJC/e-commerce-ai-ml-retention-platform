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

      {page === "dashboard" && <Dashboard />}

      {page === "customer" && <CustomerAnalysis />}
    </div>
  );
}

export default App;