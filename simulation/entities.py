from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Patient:
    patient_id: int
    arrival_hour: int
    acuity_level: int
    estimated_service_time: float
    started_hour: int | None = None
    completed_hour: int | None = None
    has_error: bool = False


@dataclass
class Resources:
    beds: int
    nurses: int
    doctors: int


@dataclass
class RandomEvent:
    name: str
    severity: float
    remaining_hours: int


@dataclass
class KPIResult:
    door_to_doctor: float
    length_of_stay: float
    throughput: int
    error_rate: float
    treated_patients: int
    untreated_patients: int
    event_log: list[str] = field(default_factory=list)
