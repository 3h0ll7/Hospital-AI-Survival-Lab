from fastapi import APIRouter

from app.models.schemas import SimulationRequest, SimulationResponse
from app.services.lab_service import SurvivalLabService

router = APIRouter(prefix="/api")
service = SurvivalLabService()


@router.post("/simulate", response_model=SimulationResponse)
def run_simulation(payload: SimulationRequest) -> dict:
    return service.run_iteration(payload)
