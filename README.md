# E-Commerce AI/ML-Based Customer Retention & Churn Analytics Platform

An AI-powered customer retention platform that combines **machine learning churn prediction**, **SHAP explainability**, **risk-based agentic workflows**, **Retrieval-Augmented Generation (RAG)**, and **Supabase** to generate evidence-based customer retention recommendations.

The system analyzes individual customer behaviour, estimates churn risk, explains the model prediction, retrieves relevant customer-retention knowledge, and generates targeted retention strategies based on the customer's risk level.

## Overview

Traditional churn prediction systems typically answer:

> **"Is this customer likely to churn?"**

This project extends that workflow by answering:

> **"Why is this customer at risk, what evidence supports the interpretation, and what retention strategy should be considered?"**

The platform combines deterministic machine-learning outputs with an LLM-based recommendation layer and external retention knowledge retrieved through RAG.

### Core Pipeline

```text
Customer Data
     │
     ▼
Machine Learning Model
     │
     ├── Churn Prediction
     ├── Churn Probability
     └── Risk Level
             │
             ▼
       SHAP Explainability
             │
             ├── Positive Contributors
             └── Negative Contributors
             │
             ▼
      Risk-Based Routing
       ┌─────┼─────┐
       ▼     ▼     ▼
     High  Medium Low
       │     │     │
       ▼     ▼     ▼
     RAG   RAG   RAG
       │     │     │
       └─────┼─────┘
             ▼
     Retention Knowledge
             │
             ▼
       Gemini LLM
             │
             ▼
 Evidence-Based Retention
      Recommendation
             │
             ▼
          FastAPI
             │
       ┌─────┴─────┐
       ▼           ▼
   Frontend     Supabase
   Dashboard    Persistence
```

## Features

### 1. Customer Churn Prediction

The machine-learning pipeline predicts whether a customer is likely to churn and produces a churn probability.

The system uses behavioural and customer-level features including:

* Purchase frequency
* Monetary value
* Average order value
* Unique product categories
* Unique sellers
* Average review score
* Late-delivery ratio
* Average installments
* Maximum installments
* Payment method count
* Preferred payment type
* Customer state
* Latitude
* Longitude

### 2. Risk Classification

Customers are assigned to one of three risk levels:

* **Low Risk**
* **Medium Risk**
* **High Risk**

The risk level is determined from the model's churn probability and is subsequently used to route the customer through a specialized workflow.

### 3. SHAP Explainability

The platform uses **SHAP (SHapley Additive exPlanations)** to explain individual model predictions.

For each customer, the system identifies model-attributed factors that:

* Increase predicted churn risk
* Decrease predicted churn risk

The system explicitly treats SHAP values as **model attribution rather than causal evidence**.

### 4. Risk-Based Agentic Workflow

The application uses **LangGraph** to orchestrate the analysis workflow.

The workflow routes customers according to their predicted risk:

```text
                  ┌── High Risk ──► High-Risk RAG ──► High-Risk Recommendation
                  │
Prediction ───────┼── Medium Risk ► Medium-Risk RAG ► Medium-Risk Recommendation
                  │
                  └── Low Risk ───► Low-Risk RAG ───► Low-Risk Recommendation
```

This allows each risk segment to have a different:

* Retrieval strategy
* Retention strategy focus
* Prompt
* Recommendation approach

For example, high-risk customers can receive more proactive strategies such as win-back and reactivation interventions, while low-risk customers can receive lighter engagement and loyalty strategies.

### 5. Retrieval-Augmented Generation

The recommendation system does not rely exclusively on prompt engineering.

Instead, it retrieves external retention knowledge relevant to:

* Customer churn
* Customer retention
* Customer loyalty
* Customer engagement
* E-commerce retention
* Customer relationship management
* Win-back strategies
* Service recovery
* Targeted promotions

The retrieved knowledge is supplied to the LLM as contextual evidence before generating the recommendation.

### 6. Supabase Vector Database

Retention knowledge is stored in **Supabase PostgreSQL with pgvector**.

The RAG pipeline:

```text
Retention Documents
       │
       ▼
Document Chunking
       │
       ▼
Embedding Generation
       │
       ▼
Supabase Vector Storage
       │
       ▼
Similarity Search
       │
       ▼
Relevant Retention Knowledge
```

The project currently uses:

**`sentence-transformers/all-MiniLM-L6-v2`**

for embedding generation.

### 7. LLM Recommendation Generation

Retrieved knowledge, customer information, machine-learning predictions, and SHAP explanations are provided to **Google Gemini**.

The LLM generates a structured retention recommendation containing:

* Risk level
* Explanation
* Key risk factors
* Recommended actions

Structured output is used to keep the recommendation format consistent.

### 8. Customer and Analysis Persistence

Supabase also stores customer analysis results.

The current database structure contains:

```text
customers
    │
    │ 1-to-many
    ▼
churn_analyses
```

The `customers` table stores the customer characteristics submitted for analysis.

The `churn_analyses` table stores:

* Churn prediction
* Churn probability
* Risk level
* SHAP feature contributions
* AI retention recommendation
* Analysis timestamp

This allows historical predictions and analyses to be retained for dashboard-level analytics.

### 9. Analytics Dashboard

The frontend provides a population-level customer retention dashboard containing:

* Total customers
* Predicted churn rate
* Average churn probability
* Risk-level distribution
* Risk-segment summaries
* Customer metrics by risk level
* Aggregate SHAP feature attribution
* SHAP attribution by risk segment

It also provides an individual customer analysis interface showing:

* Machine-learning risk assessment
* Churn probability
* Individual SHAP contributions
* AI-generated retention explanation
* Recommended retention actions

## Technology Stack

### Machine Learning

* Python
* scikit-learn
* LightGBM / CatBoost
* SHAP
* Pandas
* NumPy

### AI / Agentic Workflow

* Google Gemini
* LangChain
* LangGraph
* Pydantic

### RAG

* Hugging Face Sentence Transformers
* `sentence-transformers/all-MiniLM-L6-v2`
* Vector similarity search
* Supabase pgvector

### Backend

* FastAPI
* Uvicorn
* Pydantic

### Database

* Supabase
* PostgreSQL
* pgvector

### Frontend

* React
* Dashboard-based data visualization
* REST API integration

### Deployment

* Docker

> AWS deployment is not currently implemented and is intentionally excluded from this version of the project.

## Project Structure

```text
e-commerce-ai-ml-retention-platform/
│
├── api/
│   └── main.py
│
├── src/
│   └── inference/
│       └── predictor.py
│
├── llm/
│   └── schemas.py
│
├── rag/
│   ├── documents/
│   ├── embeddings.py
│   ├── query_builder.py
│   ├── retriever.py
│   └── rag_pipeline.py
│
├── frontend/
│   └── ...
│
├── models/
│   └── ...
│
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

The exact directory structure may evolve as the project develops.

## Database Schema

### `customers`

Stores customer information submitted to the platform.

| Column                   | Type             | Description                   |
| ------------------------ | ---------------- | ----------------------------- |
| `id`                     | bigint           | Primary key                   |
| `frequency`              | integer          | Number of purchases           |
| `monetary`               | double precision | Total monetary value          |
| `avg_order_value`        | double precision | Average order value           |
| `unique_categories`      | integer          | Number of unique categories   |
| `unique_sellers`         | integer          | Number of unique sellers      |
| `avg_review_score`       | double precision | Average customer review score |
| `late_delivery_ratio`    | double precision | Ratio of late deliveries      |
| `avg_installments`       | double precision | Average payment installments  |
| `max_installments`       | double precision | Maximum payment installments  |
| `payment_method_count`   | integer          | Number of payment methods     |
| `preferred_payment_type` | text             | Preferred payment method      |
| `state`                  | text             | Customer state                |
| `latitude`               | double precision | Customer latitude             |
| `longitude`              | double precision | Customer longitude            |
| `created_at`             | timestamptz      | Record creation timestamp     |

### `churn_analyses`

Stores the results of customer churn analyses.

| Column                  | Type             | Description                  |
| ----------------------- | ---------------- | ---------------------------- |
| `id`                    | bigint           | Primary key                  |
| `customer_id`           | bigint           | References `customers.id`    |
| `churn_prediction`      | integer          | Binary churn prediction      |
| `churn_probability`     | double precision | Predicted churn probability  |
| `risk_level`            | text             | Low, Medium, or High         |
| `feature_contributions` | jsonb            | SHAP feature contributions   |
| `recommendation`        | jsonb            | Structured AI recommendation |
| `created_at`            | timestamptz      | Analysis timestamp           |

## API

The FastAPI backend exposes the main customer analysis functionality through:

```text
POST /analyze
```

Example request:

```json
{
  "frequency": 3,
  "monetary": 245.80,
  "avg_order_value": 81.93,
  "unique_categories": 3,
  "unique_sellers": 3,
  "avg_review_score": 4.5,
  "late_delivery_ratio": 0.0,
  "avg_installments": 2.0,
  "max_installments": 3.0,
  "payment_method_count": 1,
  "preferred_payment_type": "credit_card",
  "state": "SP",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

The response contains the machine-learning assessment, SHAP explanation, and AI-generated retention recommendation.

The application also provides a population-level analytics interface through the frontend.

## Running Locally

### 1. Clone the Repository

```bash
git clone <repository-url>
cd e-commerce-ai-ml-retention-platform
```

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Do not commit `.env` to the repository.

### 5. Start the Backend

```bash
uvicorn api.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

### 6. Start the Frontend

Navigate to the frontend directory and install its dependencies:

```bash
cd frontend
npm install
```

Then start the development server:

```bash
npm run dev
```

The frontend will display the customer retention dashboard and communicate with the FastAPI backend.

## Docker

The backend can also be containerized.

Build the image:

```bash
docker build -t ecommerce-retention-backend .
```

Run the container:

```bash
docker run --rm \
  --env-file .env \
  -p 8000:8000 \
  ecommerce-retention-backend
```

The backend should then be accessible at:

```text
http://localhost:8000
```

## RAG Workflow

The current RAG architecture follows:

```text
Customer Input
      │
      ▼
Churn Prediction
      │
      ▼
SHAP Explanation
      │
      ▼
Risk Classification
      │
      ▼
Risk-Specific RAG Query
      │
      ▼
Embedding Model
      │
      ▼
Supabase Vector Search
      │
      ▼
Relevant Retention Knowledge
      │
      ▼
Risk-Specific Gemini Prompt
      │
      ▼
Structured Recommendation
```

The RAG system is intentionally separated from the machine-learning model.

The ML model determines **what the model predicts**.

SHAP explains **which features contributed to that prediction**.

RAG provides **external retention knowledge**.

The LLM combines these inputs to produce **a practical recommendation**.

## Design Principles

### Machine Learning Remains the Decision Source

The LLM does not determine the churn probability or risk level.

Instead:

```text
ML Model → Prediction
SHAP     → Model Attribution
RAG      → External Knowledge
LLM      → Explanation + Recommendation
```

This separation reduces the risk of allowing the LLM to override deterministic model outputs.

### Risk-Specific Recommendations

Different risk levels require different retention strategies.

**High Risk**

* Win-back strategies
* Reactivation
* Service recovery
* Targeted incentives
* Immediate intervention

**Medium Risk**

* Engagement campaigns
* Personalized recommendations
* Repeat-purchase incentives
* Satisfaction improvement
* Preventive intervention

**Low Risk**

* Loyalty engagement
* Personalized recommendations
* Cross-selling
* Lightweight promotions
* Maintaining positive customer experience

## Future Improvements

Potential future extensions include:

* AWS deployment
* Automated retention campaign tracking
* Measuring recommendation effectiveness
* Feedback loops from actual customer outcomes
* A/B testing of retention strategies
* More diverse retention knowledge sources
* Improved document ranking and retrieval
* Customer segmentation
* Temporal churn analysis
* Recommendation outcome monitoring
* Model retraining pipelines
* Production monitoring and observability

## Project Goal

The goal of this project is to demonstrate an end-to-end **AI-driven customer retention system** that moves beyond simply predicting churn.

The platform combines:

```text
Predict
   ↓
Explain
   ↓
Retrieve Evidence
   ↓
Reason
   ↓
Recommend
   ↓
Store
   ↓
Analyze
```

This creates a practical bridge between **machine-learning-based churn prediction** and **actionable customer retention decision support**.
