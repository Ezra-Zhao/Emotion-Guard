"""Classroom session: register people, ingest observations, aggregate mood."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List

from .schemas import Emotion, Observation, Person


class ClassroomSession:
    """Holds one classroom's people and their emotion observations."""

    def __init__(self, name: str = "Sunshine Class") -> None:
        self.name = name
        self.persons: Dict[str, Person] = {}
        self.observations: List[Observation] = []

    def add_person(self, person: Person) -> None:
        self.persons[person.person_id] = person

    def ingest(self, obs: Observation) -> None:
        if obs.person.person_id not in self.persons:
            raise ValueError(f"Unknown person: {obs.person.person_id}")
        self.observations.append(obs)

    def history(self, person_id: str) -> List[Observation]:
        """Observations for one person, oldest first."""
        return sorted(
            (o for o in self.observations if o.person.person_id == person_id),
            key=lambda o: o.timestamp,
        )

    def mood_summary(self, person_id: str) -> Dict[str, float]:
        """Fraction of each emotion for one person (0.0 if no data)."""
        hist = self.history(person_id)
        summary = {e.value: 0.0 for e in Emotion}
        if not hist:
            return summary
        counts = Counter(o.emotion for o in hist)
        return {e.value: round(counts.get(e, 0) / len(hist), 3) for e in Emotion}

    def classroom_mood(self) -> Dict[str, float]:
        """Overall emotion distribution across everyone observed."""
        summary = {e.value: 0.0 for e in Emotion}
        if not self.observations:
            return summary
        counts = Counter(o.emotion for o in self.observations)
        total = len(self.observations)
        return {e.value: round(counts.get(e, 0) / total, 3) for e in Emotion}
