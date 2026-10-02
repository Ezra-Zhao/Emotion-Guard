# Emotion-Guard

**[English](README.md)** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Português](README.pt.md) | [Русский](README.ru.md)

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Status: demo](https://img.shields.io/badge/status-demo_v0.1-orange)


**Classroom emotion monitoring for kindergarten safety — catch distress before it escalates.**

Emotion-Guard watches classroom mood through facial emotion signals (happy / calm / sad / angry)
for children and teachers, aggregates it into a live classroom dashboard, and raises early
warnings — e.g. a child sliding into sustained distress, or a teacher showing stress spikes —
so staff can do a caring check-in *before* a situation turns into an incident.

> **Project status: demo v0.1 (honest edition).**
> The end-to-end pipeline runs today on **fully synthetic data**: dummy frames, a seeded
> mock emotion classifier, and a scripted classroom scenario. No real children, no real
> images, no real model weights. What is real: face-detection plumbing (OpenCV Haar),
> the swappable classifier interface, the alert rules, and the reporting. What is still
> TODO (clearly marked): wiring in a real emotion model (`fer` / DeepFace) and on-device
> deployment. Nothing here pretends to be production-ready.

## Background

This project grew out of real work: an emotion-recognition system deployed in kindergartens
to detect whether children (and teachers) were happy, flagging sustained negative mood as
an early indicator to help prevent mistreatment and violent incidents. Emotion-Guard is a
clean-room demo rebuild of that idea — same mission, synthetic data, portfolio-ready.

## What it does

1. **Detect** faces in classroom frames (OpenCV Haar cascade; mock detector in demo).
2. **Classify** emotion per face via a swappable `EmotionClassifier` interface
   (deterministic mock by default, labeled SIMULATED).
3. **Aggregate** into per-child and classroom-wide mood summaries.
4. **Alert** on three rules:
   - `sustained_negative_mood` — a child shows sad/angry across most recent observations
     (warning → critical as it persists);
   - `teacher_negative_spike` — a teacher flashes anger/stress (itself a safety signal);
   - `sudden_mood_swing` — happy → angry within minutes (watch flag).
5. **Report** — console dashboard, `classroom_report.json`, and a one-page `report.html`.

## Architecture

```
                    +------------------+
                    | Classroom frames |
                    |  (dummy in demo) |
                    +--------+---------+
                             |
                    +--------v---------+      +-------------------+
                    |  Face detection  |----->| MockEmotionClassifier (seeded)
                    | Haar / Mock      |      |  or FERClassifier (TODO: real model)
                    +--------+---------+      +---------+---------+
                             |                          |
                    +--------v--------------------------v--------+
                    |            ClassroomSession                |
                    |   per-person histories + mood aggregates   |
                    +------------------------+------------------+
                                             |
                              +--------------v--------------+
                              |         AlertEngine         |
                              | sustained / spike / swing |
                              +--------------+--------------+
                                             |
                    +------------+-----------+-----------+
                    |            |                       |
              console       report.json             report.html
```

## Quickstart

```bash
pip install -r requirements.txt

# Run the simulated school-day demo (8 children + 1 teacher, scripted story)
python examples/demo.py
# -> console dashboard + examples/output/classroom_report.json + report.html

# Run the test suite
python -m pytest tests/ -q
```

The demo story is scripted so every rule fires visibly: Child-04 slides into afternoon
distress (critical), Teacher-01 flashes anger once (warning), Child-02 swings happy→angry
in 20 minutes (watch).

## Swapping in a real model

`EmotionClassifier` is a protocol — implement `classify(face_image) -> EmotionResult`
and drop it in. `classifier.FERClassifier` documents the integration path
(`fer` or `deepface`, with the 7-emotion → 4-class mapping). Keep `simulated=False`
on real results so downstream code can distinguish them.

## Ethics & privacy

- **Demo contains zero real children's images.** All frames are synthetic; all
  "people" are generated IDs.
- **Intended use is strictly opt-in**: deployment in a real kindergarten requires
  written parental consent, a published data-retention policy, on-premise processing
  (no cloud upload of children's faces), and human review of every alert — the system
  *suggests check-ins*, it never makes disciplinary decisions.
- Emotion AI has known accuracy and bias limitations across ages and ethnicities;
  treat every output as a weak signal, not ground truth.

## Roadmap

- [ ] Wire `fer` / DeepFace real classifier; benchmark on a public FER dataset
- [ ] drowsiness / inattention signals as additional features
- [ ] On-device packaging (Jetson / Raspberry Pi) for classroom deployment
- [ ] Alert delivery (SMS / staff app push) with quiet-hours policy
- [ ] Longitudinal mood trends per child (privacy-preserving aggregates only)

## License

MIT — see [LICENSE](LICENSE).
