from __future__ import annotations

from economic_engine.models import AgentEconomics


class EconomicEngine:
    def __init__(self, config: dict):
        self.config = config

    def initialize_agent(self, name: str) -> AgentEconomics:
        return AgentEconomics(name=name, balance=self.config["initial_capital"], burn_rate=self.config["hourly_burn_rate"])

    def charge_usage(self, economics: AgentEconomics, tokens: int, api_calls: int, simulation_runs: int) -> float:
        token_cost = tokens * self.config["token_cost"]
        api_cost = api_calls * self.config["api_call_cost"]
        run_cost = simulation_runs * self.config["simulation_run_cost"]
        charge = token_cost + api_cost + run_cost

        economics.token_spend += token_cost
        economics.api_spend += api_cost
        economics.simulation_spend += run_cost
        economics.total_cost += charge
        economics.balance -= charge
        return charge

    def apply_burn_rate(self, economics: AgentEconomics, hours: float) -> float:
        burn_cost = economics.burn_rate * hours
        economics.total_cost += burn_cost
        economics.balance -= burn_cost
        economics.survival_time_hours += hours
        return burn_cost

    def reward(self, economics: AgentEconomics, quality_score: float, impact_factor: float) -> float:
        payment = quality_score * impact_factor
        economics.rewards_earned += payment
        economics.balance += payment
        if economics.total_cost > 0:
            economics.profit_margin = (economics.rewards_earned - economics.total_cost) / economics.total_cost
        return payment

    def invest_in_upgrade(self, economics: AgentEconomics, expected_roi: float) -> bool:
        invest_cfg = self.config["investment"]
        cost = invest_cfg["skill_upgrade_cost"]
        if economics.balance < cost:
            return False

        economics.balance -= cost
        economics.total_cost += cost
        economics.roi_history.append(expected_roi)
        economics.reputation_score += min(5.0, expected_roi * 10)
        return True

    def quality_score_from_kpis(self, kpis: dict) -> float:
        multipliers = self.config["reward_multipliers"]
        door_component = max(0, 1 - (kpis["door_to_doctor"] / 6)) * multipliers["door_to_doctor"]
        los_component = max(0, 1 - (kpis["length_of_stay"] / 14)) * multipliers["length_of_stay"]
        throughput_component = min(1.5, kpis["throughput"] / 100) * multipliers["throughput"]
        safety_component = max(0, 1 - kpis["error_rate"]) * multipliers["error_rate"]
        return round((door_component + los_component + throughput_component + safety_component) / 4, 4)
