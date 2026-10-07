from typing import Optional, List
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    days_left: float = Field(ge=0)
    progress: float = Field(ge=0, le=100)
    expected_progress: float = Field(ge=0, le=100)
    priority: int = Field(ge=1)
    dependencies: int = Field(ge=0)
    previous_delays: int = Field(ge=0)
    team_workload: float = Field(ge=0, le=1)


class PredictionResponse(BaseModel):
    risk_score: float
    risk_label: str
    progress_gap: float
    reasons: List[str]
    recommended_actions: List[str]


class WhatIfRequest(BaseModel):
    task_id: Optional[str] = None
    days_left: float = Field(ge=0)
    progress: float = Field(ge=0, le=100)
    expected_progress: float = Field(ge=0, le=100)
    priority: int = Field(ge=1)
    dependencies: int = Field(ge=0)
    previous_delays: int = Field(ge=0)
    team_workload: float = Field(ge=0, le=1)


class WhatIfResponse(BaseModel):
    current_risk: float
    scenario_risk: float
    risk_change: float
    current_label: str
    scenario_label: str
    interpretation: str