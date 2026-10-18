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

export interface ChurnProbabilityBucket {
  probability_range: string;
  customer_count: number;
}

export interface RiskSegmentSummary {
  customer_count: number;
  avg_churn_probability: number;
  avg_frequency: number;
  avg_monetary: number;
  avg_review_score: number;
  avg_late_delivery_ratio: number;
}

export interface RiskFactor {
  feature: string;
  total_abs_shap: number;
}

export interface AnalyticsResponse {
  overview: AnalyticsOverview;
  risk_distribution: RiskDistribution;
  churn_probability_distribution: ChurnProbabilityBucket[];
  risk_segment_summary: Record<string, RiskSegmentSummary>;
  customer_metrics_by_risk: Record<string, RiskSegmentSummary>;
  top_risk_factors: RiskFactor[];
  risk_factors_by_risk_level: Record<string, RiskFactor[]>;
}

export async function getAnalytics(): Promise<AnalyticsResponse> {
  const response = await api.get("/analytics");

  return response.data;
}