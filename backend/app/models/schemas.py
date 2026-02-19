from __future__ import annotations

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    rounds: int = Field(default=1, ge=1, le=72)
    agent_names: list[str] = Field(default_factory=lambda: ["Triage Optimizer", "Flow Marshal"])
    beds: int = Field(default=20, ge=1)
    nurses: int = Field(default=12, ge=1)
    doctors: int = Field(default=6, ge=1)
    tokens_used: int = Field(default=1500, ge=0)
    api_calls: int = Field(default=15, ge=0)
    simulation_runs: int = Field(default=1, ge=1)
    seed: int | None = None


class AgentMetrics(BaseModel):
    balance: float
    burn_rate: float
    profit_margin: float
    survival_time: float
    reputation_score: float
    bankrupt: bool


class AgentRoundResult(BaseModel):
    round: int
    agent_name: str
    decision: str
    payment: float
    kpis: dict
    metrics: AgentMetrics
    cost_breakdown: dict
    decision_logs: list[dict]


class SimulationResponse(BaseModel):
    rounds: int
    leaderboard: list[dict]
    results: list[AgentRoundResult]
