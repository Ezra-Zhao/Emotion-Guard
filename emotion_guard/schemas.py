"""Core data models for Emotion-Guard."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Emotion(str, Enum):
    """The four emotion classes the system tracks."""

    HAPPY = "happy"
    CALM = "calm"
    SAD = "sad"
    ANGRY = "angry"

    @property
    def is_negative(self) -> bool:
        return self in (Emotion.SAD, Emotion.ANGRY)


class Role(str, Enum):
    CHILD = "child"
    TEACHER = "teacher"


@dataclass(frozen=True)
class FaceBox:
    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True)
class EmotionResult:
    emotion: Emotion
    confidence: float
    simulated: bool = False  # True when produced by the mock classifier


@dataclass(frozen=True)
class Person:
    person_id: str  # e.g. "C-01" (child) or "T-01" (teacher). Demo IDs only.
    name: str
    role: Role


@dataclass(frozen=True)
class Observation:
    person: Person
    timestamp: datetime
    emotion: Emotion
    confidence: float
    simulated: bool = False


@dataclass(frozen=True)
class Alert:
    level: str  # "watch" | "warning" | "critical"
    person: Person
    message: str
    timestamp: datetime
    rule: str
