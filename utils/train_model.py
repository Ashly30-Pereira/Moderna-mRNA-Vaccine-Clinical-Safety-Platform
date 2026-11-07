import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("data/patient_records.csv")

# ----------------------------
# Handle Missing Values
# ----------------------------

df["Prior_Reaction_History"] = df["Prior_Reaction_History"].fillna("None")

# ----------------------------
# Encode Categorical Columns
# ----------------------------

condition_encoder = LabelEncoder()
reaction_encoder = LabelEncoder()

df["Pre_Existing_Conditions"] = condition_encoder.fit_transform(
    df["Pre_Existing_Conditions"]
)

df["Prior_Reaction_History"] = reaction_encoder.fit_transform(
    df["Prior_Reaction_History"]
)

# ----------------------------
# Features
# ----------------------------

X = df[
    [
        "Age",
        "Biomarker_Level",
        "Pre_Existing_Conditions",
        "Vaccine_Dose_mcg",
        "Prior_Reaction_History"
    ]
]

# Target

y = df["Reaction_Score"]

# ----------------------------
# Train Test Split
# ----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ----------------------------
# Model
# ----------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# Accuracy
# ----------------------------

pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

print("Accuracy :", round(accuracy * 100, 2), "%")

# ----------------------------
# Save Everything
# ----------------------------

joblib.dump(model, "models/risk_model.pkl")
joblib.dump(condition_encoder, "models/condition_encoder.pkl")
joblib.dump(reaction_encoder, "models/reaction_encoder.pkl")

print("Model Saved Successfully")