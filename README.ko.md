# Emotion-Guard

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | **[한국어](README.ko.md)** | [Español](README.es.md) | [Português](README.pt.md) | [Русский](README.ru.md)

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Status: demo](https://img.shields.io/badge/status-demo_v0.1-orange)


**유치원 교실 감정 모니터링으로 아동 안전 지키기 — 악화되기 전에 이상 신호 포착.**

Emotion-Guard는 표정 신호(기쁨/평온/슬픔/분노)로 아동과 교사의 교실 분위기를 살피고, 실시간 대시보드로 집계한 뒤 조기 경고를 보냅니다. 예컨대 지속적인 고통에 빠지는 아동이나 스트레스 급증이 나타나는 교사 등 — 상황이 사건으로 번지기 *전에* 교직원이 따뜻하게 확인할 수 있도록 합니다.

> **프로젝트 상태: 데모 v0.1(정직 에디션).**
> 엔드투엔드 파이프라인은 현재 **완전 합성 데이터**에서 동작합니다: 더미 프레임, 시드 고정 목 감정 분류기, 각본이 있는 교실 시나리오. 실제 아동도, 실제 이미지도, 실제 모델 가중치도 없습니다. 실제로 동작하는 부분: 얼굴 검출 파이프라인(OpenCV Haar), 교체 가능한 분류기 인터페이스, 알림 규칙, 리포팅. 아직 TODO(명시): 실제 감정 모델(`fer`/DeepFace) 연결과 온디바이스 배포. 여기 있는 어떤 것도 상용 준비가 된 척하지 않습니다.

## 배경

이 프로젝트는 실제 업무에서 나왔습니다: 유치원에 배치된 감정 인식 시스템으로, 아동(과 교사)이 행복한지 감지하고 지속적인 부정적 기분을 조기 지표로 표시하여 학대와 폭력 사건 예방에 기여했습니다. Emotion-Guard는 그 아이디어의 클린룸 데모 재구축입니다 — 같은 사명, 합성 데이터, 포트폴리오용.

## 기능

1. **검출**: 교실 프레임에서 얼굴 검출(OpenCV Haar cascade, 데모에서는 mock 검출기).
2. **분류**: 교체 가능한 `EmotionClassifier` 인터페이스로 얼굴별 감정 분류(기본값은 결정적 mock, SIMULATED 라벨).
3. **집계**: 아동별 및 학급 전체 기분 요약으로 집계.
4. **알림**(3가지 규칙):
   - `sustained_negative_mood` — 최근 관측에서 아동이 지속적으로 슬픔/분노 표시(지속되면 warning → critical로 격상);
   - `teacher_negative_spike` — 교사가 순간적으로 분노/스트레스를 표출(그 자체가 안전 신호);
   - `sudden_mood_swing` — 수 분 내 기쁨 → 분노(주시 플래그).
5. **리포트** — 콘솔 대시보드, `classroom_report.json`, 한 페이지 `report.html`.

## 아키텍처

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

## 빠른 시작

```bash
pip install -r requirements.txt

# 시뮬레이션 등원일 데모 실행(아동 8명 + 교사 1명, 각본 있음)
python examples/demo.py
# -> 콘솔 대시보드 + examples/output/classroom_report.json + report.html

# 테스트 스위트 실행
python -m pytest tests/ -q
```

데모 스토리는 각 규칙이 눈에 띄게 발동되도록 각본화되어 있습니다: Child-04는 오후에 고통에 빠지고(critical), Teacher-01은 한 번 분노를 표출하며(warning), Child-02는 20분 안에 기쁨→분노로 변합니다(watch).

## 실제 모델 연결

`EmotionClassifier`는 프로토콜입니다 — `classify(face_image) -> EmotionResult`를 구현해서 끼우면 됩니다. `classifier.FERClassifier`에 통합 경로가 문서화되어 있습니다(`fer` 또는 `deepface`, 7감정 → 4클래스 매핑 포함). 실제 결과에는 `simulated=False`를 유지하여 다운스트림 코드가 구분할 수 있게 하세요.

## 윤리 및 개인정보

- **데모에 실제 아동 이미지는 전혀 없습니다.** 모든 프레임은 합성이며, 모든 "사람"은 생성된 ID입니다.
- **의도된 용도는 엄격한 옵트인**: 실제 유치원 배치에는 학부모 서면 동의, 공개된 데이터 보존 정책, 온프레미스 처리(아동 얼굴의 클라우드 업로드 금지), 모든 알림의 인간 검토가 필요합니다 — 시스템은 *확인을 제안*할 뿐, 징계 결정을 내리지 않습니다.
- 감정 AI는 연령과 인종에 걸친 정확도와 편향의 알려진 한계가 있습니다. 모든 출력을 정답이 아닌 약한 신호로 다루세요.

## 로드맵

- [ ] `fer`/DeepFace 실제 분류기 연결, 공개 FER 데이터셋으로 벤치마크
- [ ] 졸음/주의산만 신호를 추가 피처로
- [ ] 온디바이스 패키징(Jetson/Raspberry Pi)으로 교실 배포
- [ ] 알림 전달(SMS/교직원 앱 푸시), 조용한 시간 정책 포함
- [ ] 아동별 장기 기분 추세(개인정보 보호 집계만)

## 라이선스

MIT — [LICENSE](LICENSE) 참조.
