from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from agents.example_agent import TriageOptimizerAgent
from economic_engine.engine import EconomicEngine
from simulation.engine import ERSimulationEngine
from simulation.entities import Resources

from app.models.schemas import SimulationRequest
from app.services.config_loader import load_config


class SurvivalLabService:
    def __init__(self) -> None:
        self.config = load_config()
        self.econ_engine = EconomicEngine(self.config)

    def run_iteration(self, request: SimulationRequest) -> dict:
        round_results: list[dict] = []
        econ_by_agent = {name: self.econ_engine.initialize_agent(name) for name in request.agent_names}
        agents = {name: TriageOptimizerAgent(name=name) for name in request.agent_names}

        sim_cfg = self.config["simulation"]

        for round_idx in range(1, request.rounds + 1):
            for name in request.agent_names:
                agent = agents[name]
                economics = econ_by_agent[name]
                if economics.bankrupt:
                    continue

                decision = agent.decide(balance=economics.balance, burn_rate=economics.burn_rate)
                if decision.action == "invest" and self.econ_engine.invest_in_upgrade(economics, decision.expected_roi):
                    agent.skill_level += self.config["investment"]["efficiency_gain"]

                self.econ_engine.charge_usage(
                    economics,
                    tokens=request.tokens_used,
                    api_calls=request.api_calls,
                    simulation_runs=request.simulation_runs,
                )
                self.econ_engine.apply_burn_rate(economics, hours=sim_cfg["shift_hours"])

                staffing = agent.allocate_staff(request.beds, request.nurses, request.doctors)
                sim_engine = ERSimulationEngine(
                    shift_hours=sim_cfg["shift_hours"],
                    patients_per_hour=sim_cfg["patients_per_hour"],
                    event_probabilities=sim_cfg["event_probabilities"],
                    seed=(request.seed + round_idx if request.seed is not None else None),
                )
                triage_efficiency = agent.optimize_triage()
                workflow_efficiency = agent.redesign_workflow()

                sim_result = sim_engine.run(
                    resources=Resources(**staffing),
                    triage_efficiency=triage_efficiency,
                    workflow_efficiency=workflow_efficiency,
                )
                kpis = sim_engine.result_to_dict(sim_result)
                quality_score = self.econ_engine.quality_score_from_kpis(kpis)
                payment = self.econ_engine.reward(economics, quality_score, self.config["impact_factor"])

                round_results.append(
                    {
                        "round": round_idx,
                        "agent_name": name,
                        "decision": decision.action,
                        "payment": round(payment, 3),
                        "kpis": kpis,
                        "metrics": {
                            "balance": round(economics.balance, 3),
                            "burn_rate": economics.burn_rate,
                            "profit_margin": round(economics.profit_margin, 3),
                            "survival_time": economics.survival_time_hours,
                            "reputation_score": round(economics.reputation_score, 2),
                            "bankrupt": economics.bankrupt,
                        },
                        "cost_breakdown": {
                            "token_spend": round(economics.token_spend, 3),
                            "api_spend": round(economics.api_spend, 3),
                            "simulation_spend": round(economics.simulation_spend, 3),
                            "total_cost": round(economics.total_cost, 3),
                            "rewards_earned": round(economics.rewards_earned, 3),
                        },
                        "decision_logs": [d.__dict__ for d in agent.decision_log],
                    }
                )

        leaderboard = sorted(
            [
                {
                    "agent_name": name,
                    "balance": round(economics.balance, 3),
                    "reputation_score": round(economics.reputation_score, 2),
                    "survival_time": economics.survival_time_hours,
                    "bankrupt": economics.bankrupt,
                }
                for name, economics in econ_by_agent.items()
            ],
            key=lambda x: (x["bankrupt"], -x["balance"], -x["reputation_score"]),
        )

        return {"rounds": request.rounds, "leaderboard": leaderboard, "results": round_results}
