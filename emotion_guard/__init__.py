"""Emotion-Guard: classroom emotion monitoring for kindergarten safety."""

from .schemas import Alert, Emotion, EmotionResult, FaceBox, Observation, Person, Role
from .detector import FaceDetector, HaarFaceDetector, MockFaceDetector
from .classifier import (
    EmotionClassifier,
    FERClassifier,
    MockEmotionClassifier,
    PROFILE_DISTRIBUTIONS,
)
from .classroom import ClassroomSession
from .alerts import AlertConfig, AlertEngine
from .dashboard import build_report, render_console, write_html, write_json

__all__ = [
    "Alert",
    "AlertConfig",
    "AlertEngine",
    "ClassroomSession",
    "Emotion",
    "EmotionClassifier",
    "EmotionResult",
    "FERClassifier",
    "FaceBox",
    "FaceDetector",
    "HaarFaceDetector",
    "MockEmotionClassifier",
    "MockFaceDetector",
    "Observation",
    "Person",
    "PROFILE_DISTRIBUTIONS",
    "Role",
    "build_report",
    "render_console",
    "write_html",
    "write_json",
]

__version__ = "0.1.0"
