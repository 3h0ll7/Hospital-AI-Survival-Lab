from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentDecision:
    action: str
    reason: str
    expected_roi: float


@dataclass
class HospitalAIAgent:
    name: str
    skill_level: float = 1.0
    reputation: float = 50.0
    subcontracting_enabled: bool = False
    decision_log: list[AgentDecision] = field(default_factory=list)

    def decide(self, balance: float, burn_rate: float) -> AgentDecision:
        runway = balance / burn_rate if burn_rate else 999
        if runway < 20:
            decision = AgentDecision("conserve", "Low runway: reduce experimentation spend", 0.01)
        elif balance > 7 and self.skill_level < 1.5:
            decision = AgentDecision("invest", "Strong cash position and high long-term ROI", 0.12)
        else:
            decision = AgentDecision("work", "Optimize operations for near-term payouts", 0.08)

        self.decision_log.append(decision)
        return decision

    def optimize_triage(self) -> float:
        return 1.0 + (self.skill_level - 1.0) * 0.5

    def allocate_staff(self, beds: int, nurses: int, doctors: int) -> dict[str, int]:
        if self.subcontracting_enabled and nurses < doctors * 2:
            nurses += 1
        return {"beds": beds, "nurses": nurses, "doctors": doctors}

    def redesign_workflow(self) -> float:
        return max(0.9, 1.1 - (self.reputation / 500))
