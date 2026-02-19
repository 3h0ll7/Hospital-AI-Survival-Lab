from __future__ import annotations

import random
from dataclasses import asdict

from simulation.entities import KPIResult, Patient, RandomEvent, Resources


class ERSimulationEngine:
    """Time-based ER simulation with queueing and disruption events."""

    def __init__(self, shift_hours: int, patients_per_hour: int, event_probabilities: dict[str, float], seed: int | None = None):
        self.shift_hours = shift_hours
        self.patients_per_hour = patients_per_hour
        self.event_probabilities = event_probabilities
        self._rng = random.Random(seed)

    def run(self, resources: Resources, triage_efficiency: float = 1.0, workflow_efficiency: float = 1.0) -> KPIResult:
        all_patients = self._generate_patients()
        arrivals_by_hour: dict[int, list[Patient]] = {hour: [] for hour in range(self.shift_hours)}
        for patient in all_patients:
            arrivals_by_hour[patient.arrival_hour].append(patient)

        queue: list[Patient] = []
        events: list[RandomEvent] = []
        event_log: list[str] = []

        for hour in range(self.shift_hours):
            queue.extend(arrivals_by_hour[hour])
            self._activate_event(hour, events, event_log)

            disruption = 1 + sum(event.severity for event in events)
            capacity = self._hourly_capacity(resources, disruption, workflow_efficiency)

            queue.sort(key=lambda p: (p.acuity_level, -p.estimated_service_time), reverse=True)
            for patient in queue[:capacity]:
                if patient.started_hour is None:
                    patient.started_hour = hour
                treatment_duration = max(1, round(patient.estimated_service_time * disruption))
                patient.completed_hour = min(self.shift_hours, hour + treatment_duration)
                patient.has_error = self._rng.random() < min(0.5, 0.015 * disruption * (1 / triage_efficiency))

            queue = queue[capacity:]
            self._decay_events(events)

        treated = [p for p in all_patients if p.started_hour is not None and p.completed_hour is not None]
        untreated = [p for p in all_patients if p.started_hour is None]
        if not treated:
            return KPIResult(0.0, 0.0, 0, 1.0, 0, len(untreated), event_log)

        door_to_doctor = sum((p.started_hour - p.arrival_hour) for p in treated) / len(treated)
        length_of_stay = sum((p.completed_hour - p.arrival_hour) for p in treated) / len(treated)
        error_rate = sum(1 for p in treated if p.has_error) / len(treated)

        return KPIResult(
            door_to_doctor=round(door_to_doctor, 2),
            length_of_stay=round(length_of_stay, 2),
            throughput=len(treated),
            error_rate=round(error_rate, 3),
            treated_patients=len(treated),
            untreated_patients=len(untreated),
            event_log=event_log,
        )

    def _generate_patients(self) -> list[Patient]:
        patients: list[Patient] = []
        patient_id = 0
        for hour in range(self.shift_hours):
            for _ in range(self.patients_per_hour):
                acuity = self._rng.randint(1, 5)
                patients.append(
                    Patient(
                        patient_id=patient_id,
                        arrival_hour=hour,
                        acuity_level=acuity,
                        estimated_service_time=max(0.4, self._rng.gauss(1.3 + acuity * 0.25, 0.35)),
                    )
                )
                patient_id += 1
        return patients

    def _activate_event(self, hour: int, events: list[RandomEvent], event_log: list[str]) -> None:
        if self._rng.random() < self.event_probabilities.get("mass_casualty", 0.0):
            events.append(RandomEvent("mass_casualty", 0.45, 2))
            event_log.append(f"Hour {hour}: mass_casualty")
        if self._rng.random() < self.event_probabilities.get("system_outage", 0.0):
            events.append(RandomEvent("system_outage", 0.7, 1))
            event_log.append(f"Hour {hour}: system_outage")

    @staticmethod
    def _hourly_capacity(resources: Resources, disruption: float, workflow_efficiency: float) -> int:
        gross_capacity = (resources.doctors * 2.0) + (resources.nurses * 1.0) + (resources.beds * 0.4)
        adjusted = gross_capacity * workflow_efficiency / disruption
        return max(1, int(adjusted))

    @staticmethod
    def _decay_events(events: list[RandomEvent]) -> None:
        survivors = []
        for event in events:
            event.remaining_hours -= 1
            if event.remaining_hours > 0:
                survivors.append(event)
        events[:] = survivors

    @staticmethod
    def result_to_dict(result: KPIResult) -> dict:
        return asdict(result)
