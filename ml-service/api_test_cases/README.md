# API Test Cases

These JSON files are extracted from the IEEE-CIS Fraud Detection test set
(before feature engineering).

They are provided for testing the `/predict` endpoint and validating the
end-to-end inference pipeline.

- fraud_case_*.json → Ground-truth fraud transactions
- legit_case_*.json → Ground-truth legitimate transactions

Note: Ground truth and model prediction may differ because the model is not
perfect; these files are intended for API testing rather than guaranteeing a
specific prediction.