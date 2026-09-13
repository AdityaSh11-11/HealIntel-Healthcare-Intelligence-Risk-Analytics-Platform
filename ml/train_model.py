"""
Healthcare Intelligence Platform
Enterprise Patient Risk Prediction Model

- Random Forest (multiclass)
- Clinical feature engineering
- Stratified train/test split
- Cross-validation
- Feature importance
- Probability-based risk score (0–100)
- Saves model + encoders + metrics
"""

from datetime import datetime
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# =====================================================
# PATHS
# =====================================================

BASE = Path(__file__).resolve().parents[1]

DATA_PATH = BASE / "data" / "raw" / "healthcare_dataset.csv"
MODEL_DIR = BASE / "ml"

MODEL_DIR.mkdir(exist_ok=True)

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv(DATA_PATH)

df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# =====================================================
# FEATURE ENGINEERING
# =====================================================

df["date_of_admission"] = pd.to_datetime(df["date_of_admission"])
df["discharge_date"] = pd.to_datetime(df["discharge_date"])

df["length_of_stay"] = (
    df["discharge_date"] - df["date_of_admission"]
).dt.days

# Admission month / weekday
df["admission_month"] = df["date_of_admission"].dt.month
df["admission_weekday"] = df["date_of_admission"].dt.day_name()

# High billing flag
df["high_bill"] = (df["billing_amount"] > 35000).astype(int)

# Senior citizen
df["senior_patient"] = (df["age"] >= 65).astype(int)

# Long stay
df["long_stay"] = (df["length_of_stay"] > 10).astype(int)

# =====================================================
# TARGET CREATION
# =====================================================

risk_points = (
    (df["age"] >= 65).astype(int)
    + (df["billing_amount"] > 35000).astype(int)
    + (df["test_results"] == "Abnormal").astype(int)
    + (df["length_of_stay"] > 10).astype(int)
    + (df["admission_type"] == "Emergency").astype(int)
)

# 0 = Low, 1 = Medium, 2 = High
df["risk_label"] = pd.cut(
    risk_points,
    bins=[-1, 1, 3, 5],
    labels=[0, 1, 2]
).astype(int)

# =====================================================
# FEATURES
# =====================================================

FEATURES = [
    "age",
    "gender",
    "blood_type",
    "medical_condition",
    "admission_type",
    "test_results",
    "billing_amount",
    "length_of_stay",
    "admission_month",
    "admission_weekday",
    "high_bill",
    "senior_patient",
    "long_stay",
]

TARGET = "risk_label"

X = df[FEATURES]
y = df[TARGET]

categorical = [
    "gender",
    "blood_type",
    "medical_condition",
    "admission_type",
    "test_results",
    "admission_weekday",
]

numeric = [
    "age",
    "billing_amount",
    "length_of_stay",
    "admission_month",
    "high_bill",
    "senior_patient",
    "long_stay",
]

# =====================================================
# PREPROCESSING PIPELINE
# =====================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore"),
            categorical,
        ),
        ("num", "passthrough", numeric),
    ]
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=2,
    min_samples_split=5,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1,
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ]
)

# =====================================================
# TRAIN / TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

pipeline.fit(X_train, y_train)

# =====================================================
# EVALUATION
# =====================================================

pred = pipeline.predict(X_test)
proba = pipeline.predict_proba(X_test)

accuracy = accuracy_score(y_test, pred)
f1 = f1_score(y_test, pred, average="weighted")
precision = precision_score(
    y_test,
    pred,
    average="weighted"
)

recall = recall_score(
    y_test,
    pred,
    average="weighted"
)

try:
    roc_auc = roc_auc_score(
        y_test,
        proba,
        multi_class="ovr",
    )
except Exception:
    roc_auc = None

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

cv_scores = cross_val_score(
    pipeline,
    X,
    y,
    cv=cv,
    scoring="accuracy",
)

metrics = {
    "model_name": "Random Forest Classifier",
    "accuracy": round(float(accuracy), 4),
    "precision": round(float(precision), 4),
    "recall": round(float(recall), 4),
    "f1_score": round(float(f1), 4),
    "roc_auc": None if roc_auc is None else round(float(roc_auc), 4),
    "cross_validation_accuracy": round(float(cv_scores.mean()), 4),
    "cross_validation_std": round(float(cv_scores.std()), 4),
    "train_samples": int(len(X_train)),
    "test_samples": int(len(X_test)),
    "training_date": datetime.now().strftime("%d-%m-%Y %H:%M"),
}

# =====================================================
# FEATURE IMPORTANCE
# =====================================================

encoded_names = pipeline.named_steps[
    "preprocessor"
].get_feature_names_out()

importances = pipeline.named_steps["model"].feature_importances_

feature_importance = (
    pd.DataFrame(
        {
            "feature": encoded_names,
            "importance": importances,
        }
    )
    .sort_values("importance", ascending=False)
)

feature_importance.to_csv(
    MODEL_DIR / "feature_importance.csv",
    index=False,
)

# =====================================================
# SAMPLE PREDICTIONS (For Dashboard & Power BI)
# =====================================================

risk_probability = pipeline.predict_proba(X_test)

prediction_results = X_test.copy()

prediction_results["actual_risk"] = y_test.values
prediction_results["predicted_risk"] = pred

prediction_results["risk_score"] = (
    risk_probability[:, 2] * 100
).round(2)

def assign_risk(score):
    if score >= 85:
        return "Critical Risk"
    elif score >= 65:
        return "High Risk"
    elif score >= 35:
        return "Moderate Risk"
    return "Low Risk"

prediction_results["risk_category"] = (
    prediction_results["risk_score"]
    .apply(assign_risk)
)

prediction_results["prediction_confidence"] = (
    prediction_results["risk_score"]
)

prediction_results.to_csv(
    MODEL_DIR / "sample_predictions.csv",
    index=False
)

# =====================================================
# SAVE MODEL
# =====================================================

joblib.dump(
    pipeline,
    MODEL_DIR / "risk_prediction_model.pkl",
)

with open(MODEL_DIR / "metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

# =====================================================
# PRINT REPORT
# =====================================================

print("=" * 70)
print("🏥 HEALTHCARE RISK MODEL TRAINED SUCCESSFULLY")
print("=" * 70)

print(f"Model                 : Random Forest Classifier")
print(f"Accuracy              : {accuracy:.4f}")
print(f"Precision             : {precision:.4f}")
print(f"Recall                : {recall:.4f}")
print(f"Weighted F1 Score     : {f1:.4f}")

if roc_auc:
    print(f"ROC-AUC Score         : {roc_auc:.4f}")

print(f"Cross Validation Mean : {cv_scores.mean():.4f}")
print(f"Cross Validation Std  : {cv_scores.std():.4f}")

print("\nClassification Report\n")
print(classification_report(y_test, pred))

print("\nConfusion Matrix\n")
print(confusion_matrix(y_test, pred))

print("\nTop 10 Important Features\n")
print(feature_importance.head(10))

print("\nSaved Files")
print("- risk_prediction_model.pkl")
print("- metrics.json")
print("- feature_importance.csv")
print("- sample_predictions.csv")

print("=" * 70)