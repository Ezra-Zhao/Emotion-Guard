"""Emotion classification.

The classifier is a swappable interface. The default is a deterministic
mock (clearly labeled SIMULATED) so the demo runs anywhere. Plug in a
real model via FERClassifier / DeepFaceClassifier when ready -- see
the TODO notes below.
"""

from __future__ import annotations

import random
from typing import Dict, Protocol

import numpy as np

from .schemas import Emotion, EmotionResult


class EmotionClassifier(Protocol):
    def classify(self, face_image: np.ndarray) -> EmotionResult:
        """Classify the emotion shown in a cropped face image."""
        ...


# Default emotion distributions per profile, used ONLY by the mock
# classifier to generate plausible synthetic demo data.
PROFILE_DISTRIBUTIONS: Dict[str, Dict[Emotion, float]] = {
    "typical_child": {
        Emotion.HAPPY: 0.55,
        Emotion.CALM: 0.30,
        Emotion.SAD: 0.10,
        Emotion.ANGRY: 0.05,
    },
    "distressed_child": {
        Emotion.HAPPY: 0.10,
        Emotion.CALM: 0.20,
        Emotion.SAD: 0.45,
        Emotion.ANGRY: 0.25,
    },
    "typical_teacher": {
        Emotion.HAPPY: 0.40,
        Emotion.CALM: 0.50,
        Emotion.SAD: 0.05,
        Emotion.ANGRY: 0.05,
    },
    "stressed_teacher": {
        Emotion.HAPPY: 0.15,
        Emotion.CALM: 0.35,
        Emotion.SAD: 0.20,
        Emotion.ANGRY: 0.30,
    },
}


class MockEmotionClassifier:
    """Deterministic mock classifier for demo purposes (SIMULATED).

    Draws emotions from a per-profile distribution using a seeded RNG,
    so demo runs are reproducible.
    """

    def __init__(self, profile: str = "typical_child", seed: int = 0) -> None:
        if profile not in PROFILE_DISTRIBUTIONS:
            raise ValueError(
                f"Unknown profile {profile!r}. Choose from: "
                f"{sorted(PROFILE_DISTRIBUTIONS)}"
            )
        self.profile = profile
        self._dist = PROFILE_DISTRIBUTIONS[profile]
        self._rng = random.Random(seed)

    def classify(self, face_image: np.ndarray) -> EmotionResult:
        r = self._rng.random()
        cumulative = 0.0
        chosen = Emotion.CALM
        for emotion, prob in self._dist.items():
            cumulative += prob
            if r <= cumulative:
                chosen = emotion
                break
        confidence = round(self._rng.uniform(0.62, 0.97), 3)
        return EmotionResult(emotion=chosen, confidence=confidence, simulated=True)


class FERClassifier:
    """Integration point for the real `fer` model.

    TODO(ezra): implement when wiring up the real model.
    Suggested mapping from fer's 7 emotions onto our 4 classes:

        from fer import FER
        detector = FER(mtcnn=True)
        result = detector.detect_emotions(face_bgr)[0]["emotions"]
        # angry/disgust/fear -> Emotion.ANGRY
        # sad               -> Emotion.SAD
        # happy/surprise    -> Emotion.HAPPY
        # neutral           -> Emotion.CALM

    Alternative: `deepface` (DeepFace.analyze(..., actions=["emotion"]))
    with the same dominant-emotion mapping. Keep `simulated=False` on
    real results so downstream code can tell them apart.
    """

    def __init__(self) -> None:
        raise NotImplementedError(
            "FERClassifier is an integration stub. See the docstring for "
            "how to wire in the real `fer` or `deepface` model."
        )

    def classify(self, face_image: np.ndarray) -> EmotionResult:  # pragma: no cover
        raise NotImplementedError
