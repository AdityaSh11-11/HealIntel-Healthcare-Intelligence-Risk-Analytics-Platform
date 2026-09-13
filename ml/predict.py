from pathlib import Path
import joblib
import pandas as pd

# =====================================================
# LOAD TRAINED PIPELINE MODEL
# =====================================================

BASE = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE / "ml" / "risk_prediction_model.pkl"

model = joblib.load(MODEL_PATH)


# =====================================================
# RISK CATEGORY
# =====================================================

def assign_risk_category(score: float) -> str:
    if score >= 85:
        return "Critical Risk"
    elif score >= 65:
        return "High Risk"
    elif score >= 35:
        return "Moderate Risk"
    else:
        return "Low Risk"


# =====================================================
# PREDICT SINGLE PATIENT
# =====================================================

def predict_patient_risk(patient_data: dict):

    df = pd.DataFrame([patient_data])

    # Same engineered features used during training
    df["high_bill"] = (df["billing_amount"] > 35000).astype(int)
    df["senior_patient"] = (df["age"] >= 65).astype(int)
    df["long_stay"] = (df["length_of_stay"] > 10).astype(int)

    # We don't have admission date in dashboard input,
    # so use default values matching training columns.
    df["admission_month"] = 1
    df["admission_weekday"] = "Monday"

    # Model probabilities
    probabilities = model.predict_proba(df)[0]

    # High-risk class probability
    risk_score = round(float(probabilities[2] * 100), 2)

    risk_category = assign_risk_category(risk_score)

    confidence = round(float(max(probabilities) * 100), 2)

    return risk_score, risk_category, confidence


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    sample_patient = {
        "age": 72,
        "gender": "Male",
        "blood_type": "A+",
        "medical_condition": "Diabetes",
        "billing_amount": 48000,
        "length_of_stay": 14,
        "admission_type": "Emergency",
        "test_results": "Abnormal",
    }

    score, category, confidence = predict_patient_risk(sample_patient)

    print("Risk Score :", score)
    print("Category   :", category)
    print("Confidence :", confidence)