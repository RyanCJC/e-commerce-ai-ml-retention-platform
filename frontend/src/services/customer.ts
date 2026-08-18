import api from "../api";

export interface CustomerInput {
  frequency: number;
  monetary: number;
  avg_order_value: number;
  unique_categories: number;
  unique_sellers: number;
  avg_review_score: number;
  late_delivery_ratio: number;
  avg_installments: number;
  max_installments: number;
  payment_method_count: number;
  preferred_payment_type: string;
  state: string;
  latitude: number;
  longitude: number;
}

export interface FeatureContribution {
  feature: string;
  shap_value: number;
  direction: string;
}

export interface RetentionRecommendation {
  risk_level: string;
  explanation: string;
  key_model_factors: string[];
  recommended_actions: string[];
}

export interface CustomerAnalysisResponse {
  churn_prediction: number;
  churn_probability: number;
  risk_level: string;
  feature_contributions: FeatureContribution[];
  recommendation: RetentionRecommendation;
}

export async function analyzeCustomer(
  customer: CustomerInput
): Promise<CustomerAnalysisResponse> {
  const response = await api.post(
    "/analyze",
    customer
  );

  return response.data;
}