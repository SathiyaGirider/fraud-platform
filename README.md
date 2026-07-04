# Explainable Fraud Intelligence Platform

> Most fraud detection systems give analysts a score. This platform gives them a reason.

It predicts fraudulent transactions using a Random Forest model, explains each prediction with SHAP, converts those explanations into analyst-ready investigation narratives using Groq LLaMA, and logs every decision to PostgreSQL through a FastAPI service.

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white">
  <img alt="scikit-learn" src="https://img.shields.io/badge/scikit--learn-RandomForest-F7931E?logo=scikitlearn&logoColor=white">
  <img alt="SHAP" src="https://img.shields.io/badge/SHAP-explainability-8A2BE2">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-audit_log-4169E1?logo=postgresql&logoColor=white">
  <img alt="MLflow" src="https://img.shields.io/badge/MLflow-experiment_tracking-0194E2?logo=mlflow&logoColor=white">
  <img alt="Status" src="https://img.shields.io/badge/status-active_development-yellow">
</p>

```
Transaction
    │
    ▼
Feature Engineering
    │
    ▼
Random Forest
    │
    ▼
SHAP
    │
    ▼
Narrative Generator (Groq LLaMA)
    │
    ▼
FastAPI
    │
    ▼
PostgreSQL Audit Log
```

📖 A detailed, day-by-day build log — covering every design decision, checkpoint, and tradeoff made while building this — is available in [`docs/BUILD_LOG.md`](docs/BUILD_LOG.md).

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Explainability & Compliance Layer](#explainability--compliance-layer)
- [Example Prediction](#example-prediction)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)
- [Results](#results)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Run Locally](#run-locally)
- [Future Improvements](#future-improvements)
- [Lessons Learned](#lessons-learned)
- [License](#license)
- [Contact](#contact)

---

## Problem Statement

Most fraud detection systems hand analysts a single number — a probability or a binary flag. That's not enough to act on: it doesn't say *why* a transaction looks risky, and it leaves no structured record of what drove the decision when that record is needed later for review or compliance.

This platform addresses both problems by combining explainable machine learning, automated narrative generation, and audit logging into a single fraud analysis pipeline.

## Key Features

- **Explainable predictions** — every fraud score is backed by a SHAP-derived, analyst-readable explanation, not just a number.
- **Compliance-aware narratives** — LLM-generated investigation briefs paired with deterministic references to FATF Recommendations and UK POCA 2002 s.330, kept strictly separate so regulatory language is never left to the LLM.
- **Full audit logging** — every prediction, SHAP snapshot, and narrative is stored in PostgreSQL as an immutable record.
- **FastAPI service** — REST API with Pydantic validation and auto-generated Swagger docs.
- **MLflow experiment tracking** — every training run tracked with parameters and metrics.
- **Random Forest classifier** — tuned for severe class imbalance (`class_weight='balanced'`) across 105 engineered features.
- **Chronological train/val/test split** — a deliberate departure from the random splits typically used on this dataset, chosen to eliminate temporal leakage.

## Architecture

```mermaid
flowchart LR
    A[Transaction Request] --> B[Feature Engineering]
    B --> C[Random Forest Model]
    C --> D[SHAP Explainer]
    D --> E[Narrative Translator + Groq LLaMA]
    E --> F[FastAPI Response]
    F --> G[(PostgreSQL Audit Log)]
```

**Flow:** a transaction comes in → features are engineered exactly as in training → the model produces a fraud probability → SHAP explains the prediction → the explanation is translated into an investigation narrative with compliance framing → FastAPI returns the full result and logs it to PostgreSQL.

## Dataset

[IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection) — approximately 590,000 real-world transaction records (~3.5% fraud rate), joined on transaction and identity tables. Chosen over the more commonly used European credit card fraud dataset because its raw fields (device type, email domain, card metadata, product category) support genuinely interpretable, analyst-relevant feature engineering rather than anonymized PCA components.

## Machine Learning Pipeline

- 105 engineered features covering transaction timing, amount ratios, email domain signals, device type, and card metadata. Feature engineering focused on creating behaviour-based signals rather than relying solely on raw transaction attributes.
- Chronological 80/10/10 split; features that require historical statistics (e.g. card-level averages, domain frequencies) are computed from the training partition only.
- `RandomForestClassifier(class_weight='balanced')`, chosen over SMOTE-based rebalancing since SMOTE's interpolation is incompatible with a chronological split.
- All runs tracked in MLflow (SQLite backend).

## Explainability & Compliance Layer

Raw SHAP output (`email_domain_mismatch: +0.24`, `is_night: +0.31`) isn't something an analyst can act on. This platform translates SHAP attributions into grouped, plain-language risk factors, then passes only the positive (risk-increasing) factors to an LLM to draft a short investigation brief.

Compliance references — to FATF Recommendations 10, 15, and 20, and to UK POCA 2002 s.330 — are **not** generated by the LLM. They are deterministic, pre-written Python string constants injected conditionally based on risk tier. This guarantees regulatory language is consistent and never hallucinated or paraphrased.

> This is a fraud detection system with a compliance-aware narrative layer, not an AML system. It does not make legal determinations of money laundering.

## Example Prediction

```json
{
  "transaction_id": "T_12345",
  "fraud_score": 0.91,
  "risk_tier": "HIGH RISK",
  "top_risk_factors": [
    "Transaction amount significantly exceeds this card's historical average",
    "Purchaser and recipient email domains do not match",
    "Transaction occurred outside typical hours for this card"
  ],
  "investigation_brief": "TODO: replace with a real generated narrative from the deployed service.",
  "model_version": "rf_v1"
}
```

> Illustrative only — will be replaced with a real captured response once the API is deployed.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check and model version |
| `POST` | `/predict` | Scores a transaction and returns fraud probability, risk tier, SHAP factors, and investigation narrative |
| `GET` | `/docs` | Interactive Swagger/OpenAPI documentation |

Full schemas are defined via Pydantic and browsable at `/docs`.

## Tech Stack

| Category | Tools |
|---|---|
| Modeling | Python, scikit-learn (Random Forest) |
| Explainability | SHAP |
| Narrative generation | Groq LLaMA, LangChain |
| API | FastAPI, Pydantic, Swagger |
| Database | PostgreSQL, SQLAlchemy |
| Experiment tracking | MLflow |
| Data processing | Pandas, NumPy |
| Tooling | Git |
| Containerization | Docker *(planned)* |

## Results

> Populated from the locked test-set evaluation. Not edited retroactively.

| Metric | Score |
|---|---|
| PR-AUC | `TODO` |
| ROC-AUC | `TODO` |
| Precision @ threshold | `TODO` |
| Recall @ threshold | `TODO` |
| Decision threshold | `TODO` |
| Avg. `/predict` latency (with narrative) | `TODO` ms |

## Screenshots

> To be added as the project stabilizes.

- `TODO`: Swagger UI (`/docs`)
- `TODO`: SHAP beeswarm plot (global feature importance)
- `TODO`: Sample `/predict` API response
- `TODO`: PostgreSQL audit log table
- `TODO`: MLflow experiment dashboard

## Project Structure

```
fraud-intelligence-platform/
├── README.md
├── docs/
│   └── BUILD_LOG.md
├── ml-service/
│   ├── feature_engineering.py
│   ├── shap_narratives.py
│   ├── sar_drafter.py
│   ├── main.py
│   ├── database.py
│   ├── models/
│   └── requirements.txt
└── .env.example
```

## Setup

```bash
git clone https://github.com/SathiyaGirider/fraud-intelligence-platform.git
cd fraud-intelligence-platform/ml-service

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set required environment variables in `.env`:

```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/fraud_platform
```

## Run Locally

```bash
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## Future Improvements

- Docker + Docker Compose for local orchestration
- Cloud deployment with a public health-check URL
- React analyst dashboard (case queue, narrative view, risk-tier filtering)

## Lessons Learned

- Chronological splitting is non-negotiable for transaction data — it exposed feature engineering mistakes that a random split would have hidden.
- Random Forest outperformed XGBoost's generalization on the chronological split, which shaped the final model choice over the initially planned XGBoost baseline.
- SHAP computation latency was a real bottleneck; initializing `TreeExplainer` once at module load with a fixed background sample (rather than per-request) made per-prediction explanation times practical.
- Keeping compliance language deterministic — hardcoded Python constants rather than LLM output — was the single most important architectural decision for making the narrative layer trustworthy and auditable.

## License

MIT License — see [`LICENSE`](LICENSE) for details.

## Contact

**Author:** Saty (Sathiya Girider)

- GitHub: [SathiyaGirider/fraud-intelligence-platform](https://github.com/SathiyaGirider/fraud-intelligence-platform)
- LinkedIn: `TODO`
- Email: `TODO`
