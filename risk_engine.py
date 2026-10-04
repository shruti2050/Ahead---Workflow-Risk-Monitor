import pandas as pd
from pathlib import Path


def calculate_risk(row):
    risk = 0

    # 1. Deadline pressure
    if row["days_left"] <= 2:
        risk += 25
    elif row["days_left"] <= 5:
        risk += 15

    # 2. Progress gap
    if row["progress_gap"] > 40:
        risk += 30
    elif row["progress_gap"] > 20:
        risk += 20
    elif row["progress_gap"] > 10:
        risk += 10

    # 3. Priority
    if row["priority"] == 3:
        risk += 10

    # 4. Dependencies
    risk += min(row["dependencies"] * 5, 15)

    # 5. Previous delays
    risk += min(row["previous_delays"] * 5, 15)

    # 6. Team workload
    if row["team_workload"] > 0.8:
        risk += 15
    elif row["team_workload"] > 0.6:
        risk += 8

    return min(risk, 100)


def risk_label(score):
    if score <= 30:
        return "Normal"
    elif score <= 60:
        return "Watch"
    elif score <= 80:
        return "Emerging Risk"
    else:
        return "Critical"


def ensure_progress_gap(df):
    if "progress_gap" in df.columns:
        return df

    if "expected_progress" not in df.columns:
        if "original_days" in df.columns:
            df["days_elapsed"] = (df["original_days"] - df["days_left"]).clip(lower=0)
            df["expected_progress"] = (
                (df["days_elapsed"] / df["original_days"]) * 100
            ).clip(0, 100)
        else:
            df["expected_progress"] = 0

    df["progress_gap"] = (df["expected_progress"] - df["progress"]).clip(lower=0)

    return df


def main():
    data_path = Path("data/tasks.csv")
    if not data_path.exists():
        raise FileNotFoundError(
            "Dataset not found: data/tasks.csv. Run generate_data.py first."
        )

    df = pd.read_csv(data_path)

    required_columns = {
        "days_left",
        "progress",
        "priority",
        "dependencies",
        "previous_delays",
        "team_workload",
    }
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(
            "Missing required columns in data/tasks.csv: " + ", ".join(missing)
        )

    df = ensure_progress_gap(df)
    df["risk_score"] = df.apply(calculate_risk, axis=1)
    df["risk_label"] = df["risk_score"].apply(risk_label)

    output_path = Path("data/tasks_with_risk.csv")
    df.to_csv(output_path, index=False)

    print("Risk calculation completed!")
    print()
    print(df[[
        "task_id",
        "days_left",
        "progress",
        "progress_gap",
        "priority",
        "dependencies",
        "previous_delays",
        "team_workload",
        "risk_score",
        "risk_label"
    ]].head(10))


if __name__ == "__main__":
    main()