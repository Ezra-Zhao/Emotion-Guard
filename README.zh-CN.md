# Emotion-Guard

[English](README.md) | **[简体中文](README.zh-CN.md)** | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Português](README.pt.md) | [Русский](README.ru.md)

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Status: demo](https://img.shields.io/badge/status-demo_v0.1-orange)


**幼儿园教室情绪监测，守护儿童安全——在不良情绪升级前及时发现。**

Emotion-Guard 通过面部表情信号（开心／平静／难过／生气）监测儿童与教师的课堂情绪，汇总成实时课堂仪表盘，并发出早期预警——例如某个孩子陷入持续低落，或某位教师出现压力峰值——让教职工在事态演变成事件*之前*就能去关怀问询。

> **项目状态：演示版 v0.1（诚实版）。**
> 整条流水线今天跑在**全合成数据**上：虚拟帧、固定种子的模拟情绪分类器、编排好的课堂剧本。没有真实儿童、没有真实图像、没有真实模型权重。真实的部分：人脸检测管线（OpenCV Haar）、可替换的分类器接口、告警规则和报告。仍是 TODO（明确标注）：接入真实情绪模型（`fer`／DeepFace）和端侧部署。这里没有任何东西假装自己已可投产。

## 背景

本项目源于真实工作：一套部署在幼儿园的情绪识别系统，检测儿童（与教师）是否开心，把持续的负面情绪标为早期指标，帮助预防虐待与暴力事件。Emotion-Guard 是这个想法的 clean-room 演示重构——同样的使命，合成数据，可直接放进作品集。

## 功能

1. **检测**课堂帧中的人脸（OpenCV Haar 级联；演示用 mock 检测器）。
2. **分类**每张脸的情绪，通过可替换的 `EmotionClassifier` 接口（默认确定性 mock，标注 SIMULATED）。
3. **汇总**成按儿童和全课堂的情绪摘要。
4. **告警**三条规则：
   - `sustained_negative_mood`——孩子在最近多次观察中持续难过／生气（随持续从 warning 升级为 critical）；
   - `teacher_negative_spike`——教师闪现愤怒／压力（本身即安全信号）；
   - `sudden_mood_swing`——数分钟内由开心转为愤怒（观察标记）。
5. **报告**——控制台仪表盘、`classroom_report.json` 和单页 `report.html`。

## 架构

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

## 快速上手

```bash
pip install -r requirements.txt

# 运行模拟校园日演示（8 个孩子 + 1 位教师，编排好的剧本）
python examples/demo.py
# -> 控制台仪表盘 + examples/output/classroom_report.json + report.html

# 运行测试套件
python -m pytest tests/ -q
```

演示剧本经过编排，每条规则都会明显触发：Child-04 在下午陷入低落（critical），Teacher-01 闪现一次愤怒（warning），Child-02 在 20 分钟内由开心转为愤怒（watch）。

## 接入真实模型

`EmotionClassifier` 是一个 protocol——实现 `classify(face_image) -> EmotionResult` 然后接入即可。`classifier.FERClassifier` 记录了集成路径（`fer` 或 `deepface`，含 7 情绪 → 4 分类的映射）。真实结果请保持 `simulated=False`，以便下游代码区分。

## 伦理与隐私

- **演示中零真实儿童图像。**所有帧均为合成；所有"人"都是生成的 ID。
- **预期用途严格遵循自愿加入**：在真实幼儿园部署需要家长书面同意、公开的数据保留政策、本地处理（儿童面部不上云），以及每条告警的人工复核——系统只*建议去问询*，从不做纪律处分决定。
- 情绪 AI 在不同年龄与族裔上存在已知的准确率与偏见局限；请把每条输出都当作弱信号，而非 ground truth。

## 路线图

- [ ] 接入 `fer`／DeepFace 真实分类器；在公开 FER 数据集上做 benchmark
- [ ] 困倦／注意力不集中信号作为补充特征
- [ ] 端侧打包（Jetson／Raspberry Pi），用于课堂部署
- [ ] 告警触达（短信／教职工 App 推送），带免打扰时段策略
- [ ] 按儿童的长期情绪趋势（仅隐私保护的聚合）

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
