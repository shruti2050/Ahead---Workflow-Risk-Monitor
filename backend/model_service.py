from pathlib import Path
import joblib
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "risk_model.pkl"

_model = None


def load_model():
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at: {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def build_features(
    days_left,
    progress,
    expected_progress,
    priority,
    dependencies,
    previous_delays,
    team_workload
):
    progress_gap = max(expected_progress - progress, 0)

    data = {
        "days_left": days_left,
        "progress": progress,
        "progress_gap": progress_gap,
        "priority": priority,
        "dependencies": dependencies,
        "previous_delays": previous_delays,
        "team_workload": team_workload,
    }

    model = load_model()

    if hasattr(model, "feature_names_in_"):
        columns = list(model.feature_names_in_)

        missing = [
            column
            for column in columns
            if column not in data
        ]

        if missing:
            raise ValueError(
                f"The trained model expects these features, "
                f"but they are unavailable: {missing}"
            )

        return pd.DataFrame(
            [[data[column] for column in columns]],
            columns=columns
        )

    columns = [
        "days_left",
        "progress",
        "progress_gap",
        "priority",
        "dependencies",
        "previous_delays",
        "team_workload",
    ]

    return pd.DataFrame(
        [[data[column] for column in columns]],
        columns=columns
    )


def predict(
    days_left,
    progress,
    expected_progress,
    priority,
    dependencies,
    previous_delays,
    team_workload
):
    model = load_model()

    features = build_features(
        days_left=days_left,
        progress=progress,
        expected_progress=expected_progress,
        priority=priority,
        dependencies=dependencies,
        previous_delays=previous_delays,
        team_workload=team_workload,
    )

    prediction = model.predict(features)[0]

    # Regression model
    if isinstance(
        prediction,
        (float, int, np.floating, np.integer)
    ):
        risk_score = float(prediction)
        risk_score = max(0, min(100, risk_score))

        risk_label = score_to_label(risk_score)

        return risk_score, risk_label

    # Classification model
    predicted_label = str(prediction)

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        classes = list(model.classes_)

        probability_map = {
            str(label): float(probability)
            for label, probability in zip(
                classes,
                probabilities
            )
        }

        severity = {
            "Normal": 15,
            "Watch": 40,
            "Emerging Risk": 70,
            "Critical": 95,
        }

        risk_score = sum(
            probability_map.get(label, 0)
            * severity.get(label, 50)
            for label in probability_map
        )

    else:
        risk_score = label_to_score(predicted_label)

    risk_score = max(0, min(100, float(risk_score)))

    return risk_score, normalize_label(predicted_label)


def score_to_label(score):
    if score >= 80:
        return "Critical"

    if score >= 60:
        return "Emerging Risk"

    if score >= 35:
        return "Watch"

    return "Normal"


def label_to_score(label):
    mapping = {
        "Normal": 15,
        "Watch": 40,
        "Emerging Risk": 70,
        "Critical": 95,
    }

    return mapping.get(label, 50)


def normalize_label(label):
    label = str(label).strip()

    valid_labels = {
        "Normal",
        "Watch",
        "Emerging Risk",
        "Critical",
    }

    if label in valid_labels:
        return label

    lower = label.lower()

    if "critical" in lower:
        return "Critical"

    if "emerging" in lower or "risk" in lower:
        return "Emerging Risk"

    if "watch" in lower:
        return "Watch"

    return "Normal"