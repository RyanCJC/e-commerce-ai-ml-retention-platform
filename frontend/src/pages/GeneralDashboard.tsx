import { useEffect, useState } from "react";
import { getAnalytics } from "../services/analytics";
import type { AnalyticsResponse } from "../services/analytics";
import "../App.css";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

function Dashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const data = await getAnalytics();
        setAnalytics(data);
      } catch (error) {
        console.error("Failed to load analytics:", error);
        setError("Failed to load dashboard analytics.");
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div>Loading dashboard...</div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="page">
        <div className="error-message">{error ?? "Failed to load analytics."}</div>
      </div>
    );
  }

  const riskData = [
    { name: "Low", value: analytics.risk_distribution.Low },
    { name: "Medium", value: analytics.risk_distribution.Medium },
    { name: "High", value: analytics.risk_distribution.High },
  ];

  const riskColors = ["#16a34a", "#d97706", "#dc2626"];

  const riskSummaryData = ["Low", "Medium", "High"]
    .filter((risk) => analytics.risk_segment_summary[risk] !== undefined)
    .map((risk) => {
      const data = analytics.risk_segment_summary[risk];
      return {
        risk,
        churnProbability: data.avg_churn_probability * 100,
        frequency: data.avg_frequency,
        monetary: data.avg_monetary,
        reviewScore: data.avg_review_score,
        lateDelivery: data.avg_late_delivery_ratio * 100,
      };
    });

  const topRiskFactors = analytics.top_risk_factors.map((factor) => ({
    feature: formatFeatureName(factor.feature),
    importance: factor.total_abs_shap,
  }));

  return (
    <div className="page">
      {/* HEADER */}
      <div className="page-header">
        <h1>Customer Retention Dashboard</h1>
        <p>Population-level overview of customer churn risk and model attribution.</p>
      </div>

      {/* OVERVIEW CARDS */}
      <div className="overview-grid">
        <div className="metric-card">
          <div className="metric-label">Total Customers</div>
          <div className="metric-value">{analytics.overview.total_customers}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Predicted Churn Rate</div>
          <div className="metric-value">
            {(analytics.overview.predicted_churn_rate * 100).toFixed(1)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Average Churn Probability</div>
          <div className="metric-value">
            {(analytics.overview.average_churn_probability * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* RISK SUMMARY */}
      <div className="card" style={{ marginBottom: "24px" }}>
        <h2 className="card-title">Risk Level Population</h2>
        <div className="risk-summary">
          <div className="risk-item">
            <div className="risk-item-label">Low Risk</div>
            <div className="risk-item-value risk-low">{analytics.risk_distribution.Low}</div>
          </div>
          <div className="risk-item">
            <div className="risk-item-label">Medium Risk</div>
            <div className="risk-item-value risk-medium">{analytics.risk_distribution.Medium}</div>
          </div>
          <div className="risk-item">
            <div className="risk-item-label">High Risk</div>
            <div className="risk-item-value risk-high">{analytics.risk_distribution.High}</div>
          </div>
        </div>
      </div>

      {/* RISK DISTRIBUTION GRID */}
      <div className="dashboard-grid">
        <section className="card">
          <h2 className="card-title">Risk Distribution</h2>
          <p className="card-description">Distribution of customers by predicted churn-risk level.</p>

          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {riskData.map((_, index) => (
                    <Cell key={`risk-${index}`} fill={riskColors[index]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* RISK SEGMENT TABLE */}
        <section className="card">
          <h2 className="card-title">Risk Segment Summary</h2>
          <p className="card-description">Average customer characteristics across each risk segment.</p>

          <table className="segment-table">
            <thead>
              <tr>
                <th>Risk Segment</th>
                <th>Customers</th>
                <th>Avg. Churn Prob.</th>
              </tr>
            </thead>
            <tbody>
              {["Low", "Medium", "High"].map((risk) => {
                const segment = analytics.risk_segment_summary[risk];
                if (!segment) return null;
                return (
                  <tr key={risk}>
                    <td>
                      <strong>{risk} Risk</strong>
                    </td>
                    <td>{segment.customer_count}</td>
                    <td>{(segment.avg_churn_probability * 100).toFixed(1)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>
      </div>

      {/* SEGMENT METRICS */}
      <section className="card" style={{ marginBottom: "24px" }}>
        <h2 className="card-title">Risk Segment Metrics</h2>
        <p className="card-description">Comparison of average customer behaviour across risk segments.</p>

        <div style={{ width: "100%", height: 350 }}>
          <ResponsiveContainer>
            <BarChart data={riskSummaryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="risk" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="frequency" name="Avg Frequency" fill="#6366f1" />
              <Bar dataKey="reviewScore" name="Avg Review Score" fill="#14b8a6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* MODEL ATTRIBUTION */}
      <section className="card" style={{ marginBottom: "24px" }}>
        <h2 className="card-title">Top Model-Attributed Features</h2>
        <p className="card-description">
          Features with the greatest aggregate SHAP attribution across analyzed customers.
        </p>

        <div className="interpretation-note">
          <strong>How to interpret:</strong> Feature attribution indicates how strongly a feature
          influenced the model's prediction. It does not establish that the feature caused customer churn.
        </div>

        <div style={{ width: "100%", height: 400, marginTop: "20px" }}>
          <ResponsiveContainer>
            <BarChart data={topRiskFactors} layout="vertical" margin={{ left: 40, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="feature" width={180} />
              <Tooltip />
              <Bar dataKey="importance" name="Total Absolute SHAP" fill="#6366f1" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* ATTRIBUTION BY RISK */}
      <section className="card">
        <h2 className="card-title">Model Attribution by Risk Level</h2>
        <p className="card-description">Features with the strongest model attribution within each risk segment.</p>

        <div className="overview-grid" style={{ marginTop: "20px" }}>
          {["Low", "Medium", "High"].map((risk) => {
            const factors = analytics.risk_factors_by_risk_level[risk] ?? [];

            return (
              <div className="metric-card" key={risk}>
                <h3 style={{ margin: "0 0 16px", fontSize: "16px" }}>{risk} Risk</h3>

                <div className="attribution-list">
                  {factors.length === 0 ? (
                    <p style={{ fontSize: "14px", color: "#6b7280" }}>No data available.</p>
                  ) : (
                    factors.map((factor) => (
                      <div className="attribution-row" key={factor.feature} style={{ gridTemplateColumns: "1fr auto" }}>
                        <span className="attribution-feature">{formatFeatureName(factor.feature)}</span>
                        <span className="attribution-value" style={{ color: "#111827" }}>
                          {factor.total_abs_shap.toFixed(3)}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

function formatFeatureName(feature: string): string {
  const mappings: Record<string, string> = {
    "numeric__unique_sellers": "Unique Sellers",
    "numeric__unique_categories": "Unique Categories",
    "numeric__avg_review_score": "Average Review Score",
    "numeric__monetary": "Monetary Value",
    "numeric__avg_order_value": "Average Order Value",
    "numeric__frequency": "Purchase Frequency",
    "numeric__late_delivery_ratio": "Late Delivery Ratio",
    "numeric__avg_installments": "Average Installments",
    "numeric__payment_method_count": "Payment Method Count",
    "numeric__latitude": "Latitude",
    "numeric__longitude": "Longitude",
    "categorical__state_SP": "State (SP)",
    "categorical__preferred_payment_type_debit_card": "Preferred Payment Type (Debit Card)",
    "categorical__preferred_payment_type_credit_card": "Preferred Payment Type (Credit Card)",
  };

  return (
    mappings[feature] ??
    feature
      .replace(/^numeric__/, "")
      .replace(/^categorical__/, "")
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase())
  );
}

export default Dashboard;