from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentEconomics:
    name: str
    balance: float
    burn_rate: float
    token_spend: float = 0.0
    api_spend: float = 0.0
    simulation_spend: float = 0.0
    rewards_earned: float = 0.0
    total_cost: float = 0.0
    profit_margin: float = 0.0
    survival_time_hours: float = 0.0
    reputation_score: float = 50.0
    roi_history: list[float] = field(default_factory=list)

    @property
    def bankrupt(self) -> bool:
        return self.balance <= 0
