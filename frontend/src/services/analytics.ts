import api from "../api";

export interface AnalyticsOverview {
  total_customers: number;
  predicted_churn_rate: number;
  average_churn_probability: number;
}

export interface RiskDistribution {
  Low: number;
  Medium: number;
  High: number;
}

export interface AnalyticsResponse {
  overview: AnalyticsOverview;
  risk_distribution: RiskDistribution;
  risk_segment_summary: Record<string, any>;
  customer_metrics_by_risk: Record<string, any>;
  top_risk_factors: any[];
  risk_factors_by_risk_level: Record<string, any[]>;
}

export async function getAnalytics(): Promise<AnalyticsResponse> {
  const response = await api.get("/analytics");

  return response.data;
}