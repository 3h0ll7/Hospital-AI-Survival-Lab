"""Example multi-agent, multi-round simulation loop for benchmarking."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from agents.example_agent import TriageOptimizerAgent
from economic_engine.engine import EconomicEngine
from simulation.engine import ERSimulationEngine
from simulation.entities import Resources

CONFIG_PATH = ROOT / "configs" / "economic_config.json"


def run_rounds(rounds: int = 5, seed: int = 7) -> list[dict]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    econ = EconomicEngine(config)
    sim_cfg = config["simulation"]

    agents = [TriageOptimizerAgent("Triage Optimizer"), TriageOptimizerAgent("Flow Marshal")]
    economics = {agent.name: econ.initialize_agent(agent.name) for agent in agents}
    history: list[dict] = []

    for i in range(rounds):
        for agent in agents:
            ledger = economics[agent.name]
            if ledger.bankrupt:
                continue

            decision = agent.decide(ledger.balance, ledger.burn_rate)
            if decision.action == "invest" and econ.invest_in_upgrade(ledger, decision.expected_roi):
                agent.skill_level += config["investment"]["efficiency_gain"]

            econ.charge_usage(ledger, tokens=1200, api_calls=10, simulation_runs=1)
            econ.apply_burn_rate(ledger, hours=sim_cfg["shift_hours"])

            sim = ERSimulationEngine(sim_cfg["shift_hours"], sim_cfg["patients_per_hour"], sim_cfg["event_probabilities"], seed + i)
            result = sim.run(Resources(beds=24, nurses=14, doctors=7), triage_efficiency=agent.optimize_triage(), workflow_efficiency=agent.redesign_workflow())
            reward = econ.reward(ledger, econ.quality_score_from_kpis(sim.result_to_dict(result)), config["impact_factor"])

            history.append(
                {
                    "round": i + 1,
                    "agent": agent.name,
                    "decision": decision.action,
                    "balance": round(ledger.balance, 3),
                    "throughput": result.throughput,
                    "error_rate": result.error_rate,
                    "reward": round(reward, 3),
                    "bankrupt": ledger.bankrupt,
                }
            )

    return history


if __name__ == "__main__":
    print(json.dumps(run_rounds(), indent=2))
