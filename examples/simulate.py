"""Deterministic synthetic classroom scenario generator.

Builds a scripted school-day story (seeded, reproducible):

  - 8 children + 1 teacher, 24 observation slots (08:00-16:00, every 20 min)
  - C-04 slides into sustained distress in the afternoon -> critical alert
  - T-01 (teacher) flashes anger once mid-day             -> teacher spike alert
  - C-02 swings happy -> angry within 20 minutes          -> watch alert

Everything is SYNTHETIC: dummy frames, scripted emotions, no real
children, no real images. The point is to exercise the full pipeline
(detect -> classify -> aggregate -> alert -> report) end to end.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple

import numpy as np

from emotion_guard import (
    ClassroomSession,
    Emotion,
    MockEmotionClassifier,
    MockFaceDetector,
    Observation,
    Person,
    Role,
)

SLOT_MINUTES = 20
N_SLOTS = 24
DAY_START = datetime(2026, 10, 1, 8, 0, 0)


def _slot_seed(master: int, person_id: str, slot: int) -> int:
    return hash((master, person_id, slot)) & 0xFFFFFFFF


def _scripted_emotion(person_id: str, slot: int) -> Optional[Tuple[Emotion, float]]:
    """Scripted story beats. Returns (Emotion, confidence) or None."""
    if person_id == "C-04" and slot >= 14:
        # Afternoon distress arc: alternating sad/angry.
        emo = Emotion.SAD if slot % 2 == 0 else Emotion.ANGRY
        return emo, 0.88
    if person_id == "T-01" and slot == 15:
        # Teacher stress spike.
        return Emotion.ANGRY, 0.91
    if person_id == "C-02" and slot == 10:
        return Emotion.HAPPY, 0.93
    if person_id == "C-02" and slot == 11:
        # Sudden swing: happy -> angry within one slot (20 min).
        return Emotion.ANGRY, 0.85
    return None


def generate_classroom(master_seed: int = 7) -> ClassroomSession:
    session = ClassroomSession(name="Sunshine Class")
    children = [
        Person(f"C-{i:02d}", f"Child-{i:02d}", Role.CHILD) for i in range(1, 9)
    ]
    teacher = Person("T-01", "Teacher-01", Role.TEACHER)
    for p in children + [teacher]:
        session.add_person(p)

    detector = MockFaceDetector()
    # Dummy frame: solid black. No real imagery anywhere in this demo.
    frame = np.zeros((240, 320, 3), dtype=np.uint8)

    for slot in range(N_SLOTS):
        ts = DAY_START + timedelta(minutes=slot * SLOT_MINUTES)
        for person in children + [teacher]:
            scripted = _scripted_emotion(person.person_id, slot)
            if scripted is not None:
                emotion, confidence = scripted
                simulated = True
            else:
                profile = (
                    "typical_teacher"
                    if person.role == Role.TEACHER
                    else "typical_child"
                )
                clf = MockEmotionClassifier(
                    profile=profile,
                    seed=_slot_seed(master_seed, person.person_id, slot),
                )
                box = detector.detect(frame)[0]
                face = frame[box.y : box.y + box.h, box.x : box.x + box.w]
                result = clf.classify(face)
                emotion, confidence, simulated = (
                    result.emotion,
                    result.confidence,
                    result.simulated,
                )
            session.ingest(
                Observation(
                    person=person,
                    timestamp=ts,
                    emotion=emotion,
                    confidence=confidence,
                    simulated=simulated,
                )
            )
    return session
