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

/* -------------------------------- */
/* CONSTANTS (outside the component */
/* so they are created only once)   */
/* -------------------------------- */

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

/**
 * Every field the user types into. All values are kept as strings so that a
 * field can be empty while the user is retyping it (Number("") would be 0).
 * avg_order_value is excluded because it is calculated, not typed.
 */
type FormState = Record<Exclude<keyof CustomerInput, "avg_order_value">, string>;

const INITIAL_FORM: FormState = {
  frequency: "2",
  monetary: "250",
  unique_categories: "2",
  unique_sellers: "2",
  avg_review_score: "3.5",
  late_delivery_ratio: "0.3",
  avg_installments: "0",
  max_installments: "0",
  payment_method_count: "0",
  preferred_payment_type: "credit_card",
  state: "",
  latitude: "0",
  longitude: "0",
};

/** Monetary value ÷ purchase frequency, rounded to 2 decimals. Null if it can't be calculated. */
function calculateAvgOrderValue(frequency: string, monetary: string): number | null {
  if (frequency.trim() === "" || monetary.trim() === "") return null;

  const freq = Number(frequency);
  const money = Number(monetary);

  if (!Number.isFinite(freq) || !Number.isFinite(money) || freq <= 0) return null;

  return Math.round((money / freq) * 100) / 100;
}

/* -------------------------------- */
/* PAGE                             */
/* -------------------------------- */

function CustomerAnalysis() {
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [result, setResult] = useState<CustomerAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Recalculated on every render, so it updates in real time as the user types.
  const avgOrderValue = calculateAvgOrderValue(form.frequency, form.monetary);

  function handleChange(field: keyof FormState, value: string) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  }

  async function handleAnalyze() {
    setError(null);

    if (avgOrderValue === null) {
      setError(
        "Enter a purchase frequency greater than 0 and a monetary value so the average order value can be calculated."
      );
      return;
    }

    if (!form.state) {
      setError("Please select a state.");
      return;
    }

    const toNumber = (field: keyof FormState) =>
      form[field].trim() === "" ? NaN : Number(form[field]);

    const payload: CustomerInput = {
      frequency: toNumber("frequency"),
      monetary: toNumber("monetary"),
      avg_order_value: avgOrderValue,
      unique_categories: toNumber("unique_categories"),
      unique_sellers: toNumber("unique_sellers"),
      avg_review_score: toNumber("avg_review_score"),
      late_delivery_ratio: toNumber("late_delivery_ratio"),
      avg_installments: toNumber("avg_installments"),
      max_installments: toNumber("max_installments"),
      payment_method_count: toNumber("payment_method_count"),
      preferred_payment_type: form.preferred_payment_type,
      state: form.state,
      latitude: toNumber("latitude"),
      longitude: toNumber("longitude"),
    };

    const hasInvalidNumber = Object.values(payload).some(
      (value) => typeof value === "number" && Number.isNaN(value)
    );

    if (hasInvalidNumber) {
      setError("Please fill in every field with a valid number.");
      return;
    }

    setLoading(true);

    try {
      const data = await analyzeCustomer(payload);
      setResult(data);
    } catch (err) {
      console.error("Customer analysis failed:", err);
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

  // Largest absolute SHAP value, used to scale the bars in the attribution list.
  const maxAbsShap = result
    ? Math.max(...result.feature_contributions.map((item) => Math.abs(item.shap_value)), 1e-9)
    : 1;

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
              step={1}
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
              value={avgOrderValue === null ? "" : avgOrderValue.toFixed(2)}
              readOnly
            />
            <InputField
              label="Unique Categories"
              step={1}
              value={form.unique_categories}
              onChange={(value) => handleChange("unique_categories", value)}
            />
            <InputField
              label="Unique Sellers"
              step={1}
              value={form.unique_sellers}
              onChange={(value) => handleChange("unique_sellers", value)}
            />
            <InputField
              label="Average Review Score"
              min={0}
              max={5}
              step={0.1}
              value={form.avg_review_score}
              onChange={(value) => {
                const number = Number(value);

                if (number > 5) {
                  handleChange("avg_review_score", "5");
                } else if (number < 0) {
                  handleChange("avg_review_score", "0");
                } else {
                  handleChange("avg_review_score", value);
                }
              }}
            />
            <InputField
              label="Late Delivery Ratio"
              min={0}
              max={1}
              step={0.01}
              value={form.late_delivery_ratio}
              onChange={(value) => {
                const number = Number(value);

                if (number > 1) {
                  handleChange("late_delivery_ratio", "1");
                } else if (number < 0) {
                  handleChange("late_delivery_ratio", "0");
                } else {
                  handleChange("late_delivery_ratio", value);
                }
              }}
            />
            <InputField
              label="Average Installments"
              value={form.avg_installments}
              onChange={(value) => handleChange("avg_installments", value)}
            />
            <InputField
              label="Maximum Installments"
              step={1}
              value={form.max_installments}
              onChange={(value) => handleChange("max_installments", value)}
            />
            <InputField
              label="Payment Method Count"
              step={1}
              value={form.payment_method_count}
              onChange={(value) => handleChange("payment_method_count", value)}
            />

            <div className="form-group">
              <label className="form-label" htmlFor="preferred-payment-type">
                Preferred Payment Type
              </label>
              <select
                id="preferred-payment-type"
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
              <label className="form-label" htmlFor="state">
                State
              </label>
              <select
                id="state"
                className="form-select"
                value={form.state}
                onChange={(event) => handleChange("state", event.target.value)}
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
              step={0.0001}
              value={form.latitude}
              onChange={(value) => handleChange("latitude", value)}
            />
            <InputField
              label="Longitude"
              step={0.0001}
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

          {error && <p className="error-message" style={{ marginTop: "16px" }}>{error}</p>}
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

                <div className="chart-container" style={{ margin: "20px 0" }}>
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
                            // Width is proportional to this feature's share of the largest SHAP value
                            width: `${Math.max((Math.abs(item.shap_value) / maxAbsShap) * 100, 2)}%`,
                            background: item.shap_value > 0 ? "#dc2626" : "#16a34a",
                          }}
                        ></div>
                      </div>
                      <span
                        className={`attribution-value ${
                          item.shap_value > 0 ? "attribution-positive" : "attribution-negative"
                        }`}
                      >
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
  value: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  hint?: string;
  min?: number;
  max?: number;
  step?: number;
}

function InputField({
  label,
  value,
  onChange,
  readOnly = false,
  hint,
  min,
  max,
  step = 0.1,
}: InputFieldProps) {
  return (
    <div className="form-group">
      <label className="form-label">{label}</label>
      <input
        className="form-input"
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        readOnly={readOnly}
        onChange={(event) => onChange?.(event.target.value)}
        style={readOnly ? { backgroundColor: "#f3f4f6", cursor: "not-allowed" } : undefined}
      />
      {hint && (
        <small
          style={{
            display: "block",
            marginTop: "4px",
            color: "#6b7280",
            fontSize: "12px",
          }}
        >
          {hint}
        </small>
      )}
    </div>
  );
}

/* -------------------------------- */
/* HELPERS                          */
/* -------------------------------- */

function getRiskClass(risk: string) {
  switch (risk.toLowerCase()) {
    case "high":
      return "high";
    case "medium":
      return "medium";
    case "low":
      return "low";
    default:
      return "";
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