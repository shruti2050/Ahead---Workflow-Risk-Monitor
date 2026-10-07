from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    PredictionRequest,
    PredictionResponse,
    WhatIfRequest,
    WhatIfResponse,
)

from model_service import predict

from risk_service import (
    generate_reasons,
    generate_recommendations,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "tasks_with_risk.csv"


app = FastAPI(
    title="AHEAD Workflow Risk API",
    description="Backend API for adaptive project risk and resource management.",
    version="1.0.0",
)


# React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_tasks():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}"
        )

    return pd.read_csv(DATA_PATH)


@app.get("/")
def root():
    return {
        "application": "AHEAD",
        "message": "Workflow Risk API is running",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "AHEAD Risk API",
    }


@app.get("/api/tasks")
def get_tasks():
    try:
        df = load_tasks()

        # Convert NaN to JSON-safe values
        df = df.where(pd.notnull(df), None)

        return {
            "count": len(df),
            "tasks": df.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    try:
        df = load_tasks()

        matches = df[df["task_id"].astype(str) == task_id]

        if matches.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )

        task = matches.iloc[0]

        return task.where(
            pd.notnull(task),
            None
        ).to_dict()

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post(
    "/api/predict",
    response_model=PredictionResponse
)
def predict_risk(request: PredictionRequest):

    try:
        progress_gap = max(
            request.expected_progress - request.progress,
            0
        )

        risk_score, risk_label = predict(
            days_left=request.days_left,
            progress=request.progress,
            expected_progress=request.expected_progress,
            priority=request.priority,
            dependencies=request.dependencies,
            previous_delays=request.previous_delays,
            team_workload=request.team_workload,
        )

        reasons = generate_reasons(
            days_left=request.days_left,
            progress_gap=progress_gap,
            team_workload=request.team_workload,
            dependencies=request.dependencies,
            previous_delays=request.previous_delays,
        )

        recommendations = generate_recommendations(
            risk_label,
            reasons
        )

        return {
            "risk_score": round(risk_score, 2),
            "risk_label": risk_label,
            "progress_gap": round(progress_gap, 2),
            "reasons": reasons,
            "recommended_actions": recommendations,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post(
    "/api/what-if",
    response_model=WhatIfResponse
)
def what_if(request: WhatIfRequest):

    try:
        # Current scenario
        current_score, current_label = predict(
            days_left=request.days_left,
            progress=request.progress,
            expected_progress=request.expected_progress,
            priority=request.priority,
            dependencies=request.dependencies,
            previous_delays=request.previous_delays,
            team_workload=request.team_workload,
        )

        # For now the request itself represents the scenario.
        # The React UI will later send both current and changed values.
        scenario_score = current_score
        scenario_label = current_label

        return {
            "current_risk": round(current_score, 2),
            "scenario_risk": round(scenario_score, 2),
            "risk_change": 0,
            "current_label": current_label,
            "scenario_label": scenario_label,
            "interpretation": "No changes were applied to the scenario.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/dashboard")
def dashboard():
    try:
        df = load_tasks()

        total_tasks = len(df)

        critical = int(
            (df["risk_label"] == "Critical").sum()
        )

        emerging = int(
            (df["risk_label"] == "Emerging Risk").sum()
        )

        watch = int(
            (df["risk_label"] == "Watch").sum()
        )

        normal = int(
            (df["risk_label"] == "Normal").sum()
        )

        average_risk = float(
            df["risk_score"].mean()
        )

        return {
            "total_tasks": total_tasks,
            "critical_tasks": critical,
            "emerging_risk_tasks": emerging,
            "watch_tasks": watch,
            "normal_tasks": normal,
            "average_risk": round(average_risk, 2),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )