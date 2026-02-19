from backend.app.models.schemas import SimulationRequest
from backend.app.services.lab_service import SurvivalLabService


def test_multi_agent_rounds_output_shape():
    service = SurvivalLabService()
    payload = SimulationRequest(rounds=2, agent_names=["A", "B"], seed=11)

    result = service.run_iteration(payload)

    assert result["rounds"] == 2
    assert len(result["leaderboard"]) == 2
    assert len(result["results"]) >= 2
    assert {entry["agent_name"] for entry in result["leaderboard"]} == {"A", "B"}
