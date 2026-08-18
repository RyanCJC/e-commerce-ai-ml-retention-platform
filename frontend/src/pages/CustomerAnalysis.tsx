import { useState } from "react";
import { analyzeCustomer } from "../services/customer";
import type { CustomerInput, CustomerAnalysisResponse } from "../services/customer";
import "../App.css";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

function CustomerAnalysis() {
  const [form, setForm] = useState<CustomerInput>({
    frequency: 2,
    monetary: 250,
    avg_order_value: 125,
    unique_categories: 2,
    unique_sellers: 2,
    avg_review_score: 3.5,
    late_delivery_ratio: 0.3,
    avg_installments: 0,
    max_installments: 0,
    payment_method_count: 0,
    preferred_payment_type: "credit_card",
    state: "",
    latitude: 0,
    longitude: 0,
  });

  const [result, setResult] = useState<CustomerAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleChange(field: keyof CustomerInput, value: string) {
    const numericFields: Array<keyof CustomerInput> = [
      "frequency",
      "monetary",
      "avg_order_value",
      "unique_categories",
      "unique_sellers",
      "avg_review_score",
      "late_delivery_ratio",
      "avg_installments",
      "max_installments",
      "payment_method_count",
      "latitude",
      "longitude",
    ];

    if (numericFields.includes(field)) {
      setForm((previous) => ({
        ...previous,
        [field]: Number(value),
      }));
    } else {
      setForm((previous) => ({
        ...previous,
        [field]: value,
      }));
    }
  }

  async function handleAnalyze() {
    setLoading(true);
    setError(null);

    try {
      const data = await analyzeCustomer(form);
      setResult(data);
    } catch (error) {
      console.error("Customer analysis failed:", error);
      setError("Failed to analyze customer.");
    } finally {
      setLoading(false);
    }
  }

  const attributionData =
    result?.feature_contributions.map((item) => ({
      feature: formatFeatureName(item.feature),
      shap: item.shap_value,
    })) ?? [];

    const BRAZILIAN_STATES = [
        { code: "AC", name: "Acre" },
        { code: "AL", name: "Alagoas" },
        { code: "AP", name: "Amapá" },
        { code: "AM", name: "Amazonas" },
        { code: "BA", name: "Bahia" },
        { code: "CE", name: "Ceará" },
        { code: "DF", name: "Distrito Federal" },
        { code: "ES", name: "Espírito Santo" },
        { code: "GO", name: "Goiás" },
        { code: "MA", name: "Maranhão" },
        { code: "MT", name: "Mato Grosso" },
        { code: "MS", name: "Mato Grosso do Sul" },
        { code: "MG", name: "Minas Gerais" },
        { code: "PA", name: "Pará" },
        { code: "PB", name: "Paraíba" },
        { code: "PR", name: "Paraná" },
        { code: "PE", name: "Pernambuco" },
        { code: "PI", name: "Piauí" },
        { code: "RJ", name: "Rio de Janeiro" },
        { code: "RN", name: "Rio Grande do Norte" },
        { code: "RS", name: "Rio Grande do Sul" },
        { code: "RO", name: "Rondônia" },
        { code: "RR", name: "Roraima" },
        { code: "SC", name: "Santa Catarina" },
        { code: "SP", name: "São Paulo" },
        { code: "SE", name: "Sergipe" },
        { code: "TO", name: "Tocantins" },
    ];

  return (
    <div className="page">
      {/* HEADER */}
      <div className="page-header">
        <div>
          <h1>Customer Analysis</h1>
          <p>
            Analyze an individual customer's churn risk and generate an evidence-based
            retention recommendation.
          </p>
        </div>
      </div>

      <div className="analysis-layout">
        {/* CUSTOMER INPUT */}
        <section className="card">
          <h2 className="card-title">Customer Information</h2>
          <p className="card-description">
            Enter the customer's behavioural and demographic characteristics.
          </p>

          <div className="customer-form">
            <InputField
              label="Purchase Frequency"
              value={form.frequency}
              onChange={(value) => handleChange("frequency", value)}
            />
            <InputField
              label="Monetary Value"
              value={form.monetary}
              onChange={(value) => handleChange("monetary", value)}
            />
            <InputField
              label="Average Order Value"
              value={form.avg_order_value}
              onChange={(value) => handleChange("avg_order_value", value)}
            />
            <InputField
              label="Unique Categories"
              value={form.unique_categories}
              onChange={(value) => handleChange("unique_categories", value)}
            />
            <InputField
              label="Unique Sellers"
              value={form.unique_sellers}
              onChange={(value) => handleChange("unique_sellers", value)}
            />
            <InputField
              label="Average Review Score"
              value={form.avg_review_score}
              onChange={(value) => handleChange("avg_review_score", value)}
            />
            <InputField
              label="Late Delivery Ratio"
              value={form.late_delivery_ratio}
              onChange={(value) => handleChange("late_delivery_ratio", value)}
            />
            <InputField
              label="Average Installments"
              value={form.avg_installments}
              onChange={(value) => handleChange("avg_installments", value)}
            />
            <InputField
              label="Maximum Installments"
              value={form.max_installments}
              onChange={(value) => handleChange("max_installments", value)}
            />
            <InputField
              label="Payment Method Count"
              value={form.payment_method_count}
              onChange={(value) => handleChange("payment_method_count", value)}
            />

            <div className="form-group">
              <label className="form-label">Preferred Payment Type</label>
              <select
                className="form-select"
                value={form.preferred_payment_type}
                onChange={(event) => handleChange("preferred_payment_type", event.target.value)}
              >
                <option value="credit_card">Credit Card</option>
                <option value="boleto">Boleto</option>
                <option value="voucher">Voucher</option>
                <option value="debit_card">Debit Card</option>
              </select>
            </div>

            <div className="form-group">
            <label htmlFor="state">State</label>
                <select
                    id="state"
                    value={form.state}
                    onChange={(e) => handleChange("state", e.target.value)}
                >
                    <option value="">Select a state</option>

                    {BRAZILIAN_STATES.map((state) => (
                    <option key={state.code} value={state.code}>
                        {state.name} ({state.code})
                    </option>
                    ))}
                </select>
            </div>

            <InputField
              label="Latitude"
              value={form.latitude}
              onChange={(value) => handleChange("latitude", value)}
            />
            <InputField
              label="Longitude"
              value={form.longitude}
              onChange={(value) => handleChange("longitude", value)}
            />

            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Analyze Customer"}
            </button>
          </div>

          {error && <p className="error-message" style={{ marginTop: '16px' }}>{error}</p>}
        </section>

        {/* RESULTS */}
        <div>
          {result && (
            <>
              {/* ML ASSESSMENT */}
              <section className="card prediction-card">
                <div className="prediction-header">
                  <h2 className="card-title">Machine Learning Assessment</h2>
                  <div className={`risk-badge ${getRiskClass(result.risk_level)}`}>
                    {result.risk_level} Risk
                  </div>
                </div>

                <div className="prediction-grid">
                  <div className="prediction-metric">
                    <div className="prediction-metric-label">Churn Probability</div>
                    <div className="prediction-metric-value">
                      {(result.churn_probability * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div className="prediction-metric">
                    <div className="prediction-metric-label">Prediction</div>
                    <div className="prediction-metric-value">
                      {result.churn_prediction === 1 ? "Predicted Churn" : "No Predicted Churn"}
                    </div>
                  </div>
                </div>

                <div className="probability-container">
                  <div className="probability-header">
                    <span>Probability Scale</span>
                  </div>
                  <div className="probability-bar">
                    <div
                      className="probability-fill"
                      style={{ width: `${result.churn_probability * 100}%` }}
                    ></div>
                  </div>
                </div>
              </section>

              {/* SHAP */}
              <section className="card prediction-card">
                <h2 className="card-title">Model Attribution</h2>
                <p className="card-description">
                  SHAP values indicate how each feature contributed to this individual prediction.
                </p>

                <div className="interpretation-note">
                  <strong>How to interpret:</strong> Positive SHAP values increased the
                  predicted churn risk, while negative SHAP values decreased it. These
                  attributions describe model behaviour and do not establish causation.
                </div>

                <div className="chart-container" style={{ margin: '20px 0' }}>
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={attributionData} layout="vertical" margin={{ left: 40, right: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis type="category" dataKey="feature" width={180} />
                      <Tooltip />
                      <Bar dataKey="shap" name="SHAP Value">
                        {attributionData.map((entry, index) => (
                          <Cell
                            key={`shap-${index}`}
                            fill={entry.shap > 0 ? "#dc2626" : "#16a34a"}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="attribution-list">
                  {result.feature_contributions.map((item) => (
                    <div className="attribution-row" key={item.feature}>
                      <span className="attribution-feature">{formatFeatureName(item.feature)}</span>
                      <div className="attribution-bar-container">
                        <div 
                          className="attribution-bar" 
                          style={{ 
                            width: '100%', 
                            background: item.shap_value > 0 ? '#dc2626' : '#16a34a',
                            opacity: Math.min(Math.abs(item.shap_value) * 2, 1) 
                          }}
                        ></div>
                      </div>
                      <span className={`attribution-value ${item.shap_value > 0 ? "attribution-positive" : "attribution-negative"}`}>
                        {item.shap_value > 0 ? "↑ Increases risk" : "↓ Decreases risk"}
                      </span>
                    </div>
                  ))}
                </div>
              </section>

              {/* RAG / LLM RECOMMENDATION */}
              <section className="card">
                <h2 className="card-title">AI Retention Recommendation</h2>
                <p className="card-description">
                  Retention strategy generated from the model assessment and supporting retention knowledge.
                </p>

                <div className="recommendation">
                  <div className="recommendation-section">
                    <h3>Why this customer received this assessment</h3>
                    <p>{result.recommendation.explanation}</p>
                  </div>

                  <div className="recommendation-section">
                    <h3>Key Model Factors</h3>
                    <ul className="recommendation-list">
                      {result.recommendation.key_model_factors.map((factor) => (
                        <li key={factor}>{formatFeatureName(factor)}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="recommendation-section">
                    <h3>Recommended Actions</h3>
                    <ol className="recommendation-list">
                      {result.recommendation.recommended_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ol>
                  </div>
                </div>
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/* -------------------------------- */
/* INPUT COMPONENT                  */
/* -------------------------------- */

interface InputFieldProps {
  label: string;
  value: number;
  onChange: (value: string) => void;
}

function InputField({ label, value, onChange }: InputFieldProps) {
  return (
    <div className="form-group">
      <label className="form-label">{label}</label>
      <input
        className="form-input"
        type="number"
        value={value}
        step="any"
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

/* -------------------------------- */
/* HELPERS                          */
/* -------------------------------- */

function getRiskClass(risk: string) {
  switch (risk.toLowerCase()) {
    case "high": return "high";
    case "medium": return "medium";
    case "low": return "low";
    default: return "";
  }
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

export default CustomerAnalysis;