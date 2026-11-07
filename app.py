from flask import Flask, render_template, abort
import pandas as pd 
from utils.prediction import predict_risk

from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime

app = Flask(__name__)

# Load patient records
df = pd.read_csv("data/patient_records.csv")


# ---------------- Dashboard ---------------- #

@app.route("/")
def dashboard():

    total_patients = len(df)

    high_risk = len(df[df["Reaction_Score"] == 1])
    low_risk = len(df[df["Reaction_Score"] == 0])

    avg_biomarker = round(df["Biomarker_Level"].mean(), 2)

    avg_age = round(df["Age"].mean(), 1)

    recent_patients = df.head(5).to_dict(orient="records")

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        high_risk=high_risk,
        low_risk=low_risk,
        avg_biomarker=avg_biomarker,
        avg_age=avg_age,
        recent_patients=recent_patients
    )


# ---------------- Patient List ---------------- #

@app.route("/patients")
def patients():

    patients = df.to_dict(orient="records")

    return render_template(
        "patients.html",
        patients=patients
    )


# ---------------- Patient Profile ---------------- #

@app.route("/patient/<patient_id>")
def patient_profile(patient_id):

    patient = df[df["Patient_ID"] == patient_id]

    if patient.empty:
        abort(404)

    patient = patient.iloc[0]

    return render_template(
        "patient_profile.html",
        patient=patient
    )


@app.route("/predict/<patient_id>")
def predict_patient_risk(patient_id):

    patient = df[df["Patient_ID"] == patient_id]

    if patient.empty:
        abort(404)

    patient = patient.iloc[0]


    # Prepare input for ML model

    input_data = [
        patient["Age"],
        patient["Biomarker_Level"],
        patient["Pre_Existing_Conditions"],
        patient["Vaccine_Dose_mcg"],
        patient["Prior_Reaction_History"]
    ]


    risk, confidence = predict_risk(input_data)


    return render_template(
        "prediction.html",
        patient=patient,
        risk=risk,
        confidence=confidence
    ) 
    
@app.route("/dosage/<patient_id>")
def dosage_recommendation(patient_id):

    patient = df[df["Patient_ID"] == patient_id]

    if patient.empty:
        abort(404)

    patient = patient.iloc[0]

    risk, confidence = predict_risk([
        patient["Age"],
        patient["Biomarker_Level"],
        patient["Pre_Existing_Conditions"],
        patient["Vaccine_Dose_mcg"],
        patient["Prior_Reaction_History"]
    ])

    if risk == "High Risk":

        dosage = "Low Dose (25 mcg)"
        recommendation = "Additional clinical evaluation is recommended before vaccination."

    else:

        dosage = "Standard Dose (50 mcg)"
        recommendation = "Patient is suitable for the standard vaccine dosage."

    return render_template(
        "dosage.html",
        patient=patient,
        risk=risk,
        confidence=confidence,
        dosage=dosage,
        recommendation=recommendation
    )

@app.route("/report/<patient_id>")
def generate_report(patient_id):

    patient = df[df["Patient_ID"] == patient_id]

    if patient.empty:
        abort(404)

    patient = patient.iloc[0]

    risk, confidence = predict_risk([
        patient["Age"],
        patient["Biomarker_Level"],
        patient["Pre_Existing_Conditions"],
        patient["Vaccine_Dose_mcg"],
        patient["Prior_Reaction_History"]
    ])

    if risk == "High Risk":
        dosage = "Low Dose (25 mcg)"
        recommendation = "Additional clinical evaluation is recommended."
    else:
        dosage = "Standard Dose (50 mcg)"
        recommendation = "Patient is suitable for the standard vaccine dosage."

    os.makedirs("reports", exist_ok=True)

    filename = f"reports/{patient_id}_Clinical_Report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>Moderna mRNA Vaccine Clinical Safety & Dosage Intelligence Platform</b>", styles["Title"]))

    story.append(Paragraph("<br/>", styles["BodyText"]))

    story.append(Paragraph(f"<b>Patient ID:</b> {patient.Patient_ID}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Age:</b> {patient.Age}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Biomarker Level:</b> {patient.Biomarker_Level}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Medical Condition:</b> {patient.Pre_Existing_Conditions}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Previous Reaction:</b> {patient.Prior_Reaction_History}", styles["BodyText"]))

    story.append(Paragraph("<br/>", styles["BodyText"]))

    story.append(Paragraph(f"<b>Predicted Risk:</b> {risk}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Confidence:</b> {confidence}%", styles["BodyText"]))

    story.append(Paragraph("<br/>", styles["BodyText"]))

    story.append(Paragraph(f"<b>Recommended Dosage:</b> {dosage}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Clinical Recommendation:</b> {recommendation}", styles["BodyText"]))

    story.append(Paragraph("<br/>", styles["BodyText"]))

    story.append(Paragraph(f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles["BodyText"]))

    doc.build(story)

    return send_file(filename, as_attachment=True)

@app.route("/dosage")
def dosage_home():

    patients = df.head(100).to_dict(orient="records")

    return render_template(
        "dosage_home.html",
        patients=patients
    )
    
@app.route("/analytics")
def analytics():

    risk_data = {
        "High Risk": int(
            len(df[df["Reaction_Score"] == 1])
        ),

        "Low Risk": int(
            len(df[df["Reaction_Score"] == 0])
        )
    }


    age_data = {

        "20-40": int(
            len(df[(df["Age"] >=20) & (df["Age"] <40)])
        ),

        "40-60": int(
            len(df[(df["Age"] >=40) & (df["Age"] <60)])
        ),

        "60+": int(
            len(df[df["Age"] >=60])
        )

    }


    dose_data = {

        "Low Dose": int(
            len(df[df["Vaccine_Dose_mcg"] < 50])
        ),

        "Standard Dose": int(
            len(df[
                (df["Vaccine_Dose_mcg"] >=50)
                &
                (df["Vaccine_Dose_mcg"] <=100)
            ])
        ),

        "High Dose": int(
            len(df[df["Vaccine_Dose_mcg"] >100])
        )

    }


    biomarker_average = round(
        df["Biomarker_Level"].mean(),
        2
    )


    return render_template(
        "analytics.html",
        risk_data=risk_data,
        age_data=age_data,
        dose_data=dose_data,
        biomarker_average=biomarker_average
    )   
    
@app.route("/risk_prediction")
def risk_prediction():

    total = len(df)

    high_risk = len(
        df[df["Reaction_Score"] == 1]
    )

    low_risk = len(
        df[df["Reaction_Score"] == 0]
    )

    return render_template(
        "risk_prediction.html",
        total=total,
        high_risk=high_risk,
        low_risk=low_risk
    )     
    
@app.route("/guidelines")
def guidelines():

    return render_template(
        "guidelines.html"
    )
    
@app.route("/reports")
def reports():

    reports = os.listdir("reports") if os.path.exists("reports") else []

    return render_template(
        "reports.html",
        reports=reports
    )    
    
        
# ---------------- Main ---------------- #

if __name__ == "__main__":
    app.run(debug=True)