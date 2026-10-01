"""Anomaly rules for early warning.

The point of the system: catch a child sliding into sustained distress,
or a teacher showing stress spikes, BEFORE a situation escalates.
Thresholds are configurable; the demo uses small windows so the
scripted story triggers alerts visibly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import List

from .schemas import Alert, Emotion, Observation, Role


@dataclass
class AlertConfig:
    window: int = 6  # look at the last N observations per person
    negative_threshold: int = 4  # >= K negatives in window -> warning
    critical_threshold: int = 6  # sustained negatives -> critical
    swing_window_minutes: int = 20  # happy -> angry within this -> watch


class AlertEngine:
    RULE_SUSTAINED_NEGATIVE = "sustained_negative_mood"
    RULE_TEACHER_SPIKE = "teacher_negative_spike"
    RULE_SUDDEN_SWING = "sudden_mood_swing"

    def __init__(self, config: AlertConfig | None = None) -> None:
        self.config = config or AlertConfig()

    def evaluate(self, history: List[Observation]) -> List[Alert]:
        """Evaluate one person's observation history, oldest first."""
        if not history:
            return []
        history = sorted(history, key=lambda o: o.timestamp)
        person = history[-1].person
        alerts: List[Alert] = []
        alerts.extend(self._sustained_negative(person, history))
        alerts.extend(self._sudden_swing(person, history))
        if person.role == Role.TEACHER:
            alerts.extend(self._teacher_spike(person, history))
        return alerts

    # -- rules ---------------------------------------------------------

    def _sustained_negative(
        self, person, history: List[Observation]
    ) -> List[Alert]:
        window = history[-self.config.window :]
        negatives = sum(1 for o in window if o.emotion.is_negative)
        if len(window) < self.config.negative_threshold:
            return []
        ts = window[-1].timestamp
        if negatives >= self.config.critical_threshold:
            return [
                Alert(
                    level="critical",
                    person=person,
                    message=(
                        f"{negatives}/{len(window)} recent observations show "
                        "sustained negative emotion (sad/angry). "
                        "Recommend a caring check-in."
                    ),
                    timestamp=ts,
                    rule=self.RULE_SUSTAINED_NEGATIVE,
                )
            ]
        if negatives >= self.config.negative_threshold:
            return [
                Alert(
                    level="warning",
                    person=person,
                    message=(
                        f"{negatives}/{len(window)} recent observations show "
                        "negative emotion. Keep an eye on this child."
                    ),
                    timestamp=ts,
                    rule=self.RULE_SUSTAINED_NEGATIVE,
                )
            ]
        return []

    def _teacher_spike(self, person, history: List[Observation]) -> List[Alert]:
        """A teacher flashing anger/stress is itself a safety signal."""
        window = history[-self.config.window :]
        spikes = [o for o in window if o.emotion == Emotion.ANGRY]
        if not spikes:
            return []
        latest = spikes[-1]
        return [
            Alert(
                level="warning",
                person=person,
                message=(
                    f"Teacher showed anger {len(spikes)} time(s) recently "
                    f"(latest confidence {latest.confidence:.2f}). "
                    "Consider a break / relief-teacher rotation."
                ),
                timestamp=latest.timestamp,
                rule=self.RULE_TEACHER_SPIKE,
            )
        ]

    def _sudden_swing(self, person, history: List[Observation]) -> List[Alert]:
        """Happy -> angry within a short window deserves a watch flag."""
        limit = timedelta(minutes=self.config.swing_window_minutes)
        for prev, curr in zip(history, history[1:]):
            if (
                prev.emotion == Emotion.HAPPY
                and curr.emotion == Emotion.ANGRY
                and curr.timestamp - prev.timestamp <= limit
            ):
                return [
                    Alert(
                        level="watch",
                        person=person,
                        message=(
                            "Sudden mood swing: happy -> angry within "
                            f"{self.config.swing_window_minutes} minutes."
                        ),
                        timestamp=curr.timestamp,
                        rule=self.RULE_SUDDEN_SWING,
                    )
                ]
        return []
