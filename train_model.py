import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ---------------------------------
# 1. Load dataset
# ---------------------------------

df = pd.read_csv("data/tasks_with_risk.csv")

print("Dataset loaded successfully!")
print(f"Total records: {len(df)}")


# ---------------------------------
# 2. Select ML features
# ---------------------------------

features = [
    "priority",
    "days_left",
    "progress",
    "progress_gap",
    "estimated_hours",
    "hours_spent",
    "dependencies",
    "previous_delays",
    "reassignments",
    "team_workload",
    "response_delay"
]

X = df[features]

y = df["risk_label"]


# ---------------------------------
# 3. Split data
# ---------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# ---------------------------------
# 4. Create Random Forest model
# ---------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


# ---------------------------------
# 5. Train model
# ---------------------------------

print("\nTraining model...")

model.fit(X_train, y_train)

print("Training completed!")


# ---------------------------------
# 6. Make predictions
# ---------------------------------

predictions = model.predict(X_test)


# ---------------------------------
# 7. Evaluate model
# ---------------------------------

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\nModel Accuracy:")
print(f"{accuracy * 100:.2f}%")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions
    )
)


# ---------------------------------
# 8. Feature importance
# ---------------------------------

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance:")
print(importance)


# ---------------------------------
# 9. Save model
# ---------------------------------

joblib.dump(
    model,
    "models/risk_model.pkl"
)

print("\nModel saved successfully!")
print("Location: models/risk_model.pkl")