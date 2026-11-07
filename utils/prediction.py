import joblib
import pandas as pd


# Load model
model = joblib.load("models/risk_model.pkl")

# Load encoders
condition_encoder = joblib.load(
    "models/condition_encoder.pkl"
)

reaction_encoder = joblib.load(
    "models/reaction_encoder.pkl"
)


def predict_risk(patient_data):

    age = patient_data[0]
    biomarker = patient_data[1]
    condition = patient_data[2]
    dose = patient_data[3]
    reaction = patient_data[4]


    # Handle missing conditions

    if pd.isna(condition):
        condition = "None"


    condition_encoded = condition_encoder.transform(
        [condition]
    )[0]


    # Handle missing reaction history

    if pd.isna(reaction):
        reaction = "None"


    reaction_encoded = reaction_encoder.transform(
        [reaction]
    )[0]


    # Create model input

    input_data = [[
        age,
        biomarker,
        condition_encoded,
        dose,
        reaction_encoded
    ]]


    prediction = model.predict(input_data)


    probability = model.predict_proba(input_data)


    if prediction[0] == 1:

        risk = "High Risk"

    else:

        risk = "Low Risk"


    confidence = round(
        max(probability[0]) * 100,
        2
    )


    return risk, confidence