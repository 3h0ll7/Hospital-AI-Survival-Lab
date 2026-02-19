from agents.base_agent import HospitalAIAgent


class TriageOptimizerAgent(HospitalAIAgent):
    def __init__(self, name: str = "Triage Optimizer"):
        super().__init__(name=name, subcontracting_enabled=True)

    def optimize_triage(self) -> float:
        # Specialized triage policy gives a stronger efficiency gain.
        return 1.2 + (self.skill_level - 1.0) * 0.6
