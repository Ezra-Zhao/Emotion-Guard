"""Unit tests for Emotion-Guard (all use synthetic data, no real images)."""

from datetime import datetime, timedelta

import numpy as np
import pytest

from emotion_guard import (
    AlertConfig,
    AlertEngine,
    ClassroomSession,
    Emotion,
    MockEmotionClassifier,
    MockFaceDetector,
    Observation,
    Person,
    Role,
    build_report,
)

FACE = np.zeros((96, 96, 3), dtype=np.uint8)
T0 = datetime(2026, 10, 1, 8, 0, 0)


def _person(pid="C-01", role=Role.CHILD):
    return Person(pid, f"Name-{pid}", role)


def _obs(person, emotion, slot=0, conf=0.9):
    return Observation(
        person=person,
        timestamp=T0 + timedelta(minutes=20 * slot),
        emotion=emotion,
        confidence=conf,
        simulated=True,
    )


# -- classifier --------------------------------------------------------


def test_mock_classifier_is_deterministic():
    a = MockEmotionClassifier(profile="typical_child", seed=42)
    b = MockEmotionClassifier(profile="typical_child", seed=42)
    seq_a = [a.classify(FACE).emotion for _ in range(20)]
    seq_b = [b.classify(FACE).emotion for _ in range(20)]
    assert seq_a == seq_b


def test_mock_classifier_marks_simulated():
    result = MockEmotionClassifier(seed=1).classify(FACE)
    assert result.simulated is True
    assert isinstance(result.emotion, Emotion)


def test_mock_classifier_rejects_unknown_profile():
    with pytest.raises(ValueError):
        MockEmotionClassifier(profile="nope")


def test_mock_detector_returns_centered_box():
    boxes = MockFaceDetector().detect(np.zeros((240, 320, 3), dtype=np.uint8))
    assert len(boxes) == 1
    box = boxes[0]
    assert box.w == box.h == 96


# -- alert engine ------------------------------------------------------


def _engine():
    return AlertEngine(AlertConfig(window=6, negative_threshold=4, critical_threshold=6))


def test_sustained_negative_triggers_critical():
    child = _person()
    history = [_obs(child, Emotion.SAD, slot=i) for i in range(6)]
    alerts = _engine().evaluate(history)
    assert len(alerts) == 1
    assert alerts[0].level == "critical"
    assert alerts[0].rule == AlertEngine.RULE_SUSTAINED_NEGATIVE


def test_partial_negative_triggers_warning():
    child = _person()
    history = [
        _obs(child, Emotion.HAPPY, slot=0),
        _obs(child, Emotion.HAPPY, slot=1),
        _obs(child, Emotion.SAD, slot=2),
        _obs(child, Emotion.ANGRY, slot=3),
        _obs(child, Emotion.SAD, slot=4),
        _obs(child, Emotion.SAD, slot=5),
    ]
    alerts = _engine().evaluate(history)
    assert len(alerts) == 1
    assert alerts[0].level == "warning"


def test_happy_child_no_alerts():
    child = _person()
    history = [_obs(child, Emotion.HAPPY, slot=i) for i in range(6)]
    assert _engine().evaluate(history) == []


def test_teacher_angry_spike_warns():
    teacher = _person("T-01", Role.TEACHER)
    history = [_obs(teacher, Emotion.CALM, slot=i) for i in range(5)]
    history.append(_obs(teacher, Emotion.ANGRY, slot=5))
    alerts = _engine().evaluate(history)
    rules = [a.rule for a in alerts]
    assert AlertEngine.RULE_TEACHER_SPIKE in rules
    assert any(a.level == "warning" for a in alerts)


def test_child_angry_does_not_trigger_teacher_rule():
    child = _person()
    history = [_obs(child, Emotion.ANGRY, slot=i) for i in range(2)]
    alerts = _engine().evaluate(history)
    assert all(a.rule != AlertEngine.RULE_TEACHER_SPIKE for a in alerts)


def test_sudden_swing_watch():
    child = _person()
    history = [_obs(child, Emotion.HAPPY, slot=0), _obs(child, Emotion.ANGRY, slot=1)]
    alerts = _engine().evaluate(history)
    assert any(a.rule == AlertEngine.RULE_SUDDEN_SWING for a in alerts)


def test_empty_history_no_alerts():
    assert _engine().evaluate([]) == []


# -- classroom + dashboard ---------------------------------------------


def test_classroom_mood_sums_to_one():
    session = ClassroomSession()
    child = _person()
    session.add_person(child)
    for i, emo in enumerate([Emotion.HAPPY, Emotion.HAPPY, Emotion.SAD, Emotion.CALM]):
        session.ingest(_obs(child, emo, slot=i))
    mood = session.classroom_mood()
    assert abs(sum(mood.values()) - 1.0) < 1e-6
    assert mood["happy"] == pytest.approx(0.5)


def test_ingest_unknown_person_raises():
    session = ClassroomSession()
    with pytest.raises(ValueError):
        session.ingest(_obs(_person("ghost"), Emotion.HAPPY))


def test_build_report_structure():
    session = ClassroomSession(name="Test Class")
    child = _person()
    session.add_person(child)
    session.ingest(_obs(child, Emotion.HAPPY, slot=0))
    report = build_report(session, {"C-01": []})
    assert report["classroom"] == "Test Class"
    assert report["simulated"] is True
    assert set(report["classroom_mood"]) == {"happy", "calm", "sad", "angry"}
    assert report["persons"][0]["person_id"] == "C-01"
