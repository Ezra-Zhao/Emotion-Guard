# Emotion-Guard

[English](README.md) | [简体中文](README.zh-CN.md) | **[日本語](README.ja.md)** | [한국어](README.ko.md) | [Español](README.es.md) | [Português](README.pt.md) | [Русский](README.ru.md)

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Status: demo](https://img.shields.io/badge/status-demo_v0.1-orange)


**幼稚園の教室の感情を見守り、子どもの安全を守る——問題が深刻化する前に気づく。**

Emotion-Guard は表情シグナル（happy／calm／sad／angry）で子どもと先生の教室の雰囲気を見守り、ライブのダッシュボードに集約して早期警告を出します——たとえば持続的な不調に陥る子どもや、ストレスのスパイクを見せる先生など。事態がインシデントになる*前に*、職員が温かく声をかけられるようにします。

> **プロジェクト状態：デモ v0.1（正直エディション）。**
> エンドツーエンドのパイプラインは現在、**完全な合成データ**で動作します：ダミーフレーム、シード固定のモック感情分類器、台本ありの教室シナリオ。実在の子ども、実際の画像、実際のモデルの重みは一切なし。実際に動く部分：顔検出の配管（OpenCV Haar）、差し替え可能な分類器インターフェース、アラートルール、レポート。未実装（明示）：実際の感情モデル（`fer`／DeepFace）の組み込みとオンデバイス展開。ここにあるものは、本番投入可能であるふりをしていません。

## 背景

このプロジェクトは実務から生まれました：幼稚園に導入された感情認識システムで、子ども（と先生）が幸せかどうかを検知し、持続的なネガティブな気分を早期指標としてフラグ付けし、虐待や暴力事件の防止に役立てるものです。Emotion-Guard はそのアイデアのクリーンルーム・デモ再構築——同じ使命、合成データ、ポートフォリオ対応。

## 機能

1. **検出**：教室フレーム内の顔を検出（OpenCV Haar カスケード、デモではモック検出器）。
2. **分類**：差し替え可能な `EmotionClassifier` インターフェースで顔ごとの感情を分類（デフォルトは決定論的モック、SIMULATED とラベル付け）。
3. **集計**：子ども別・クラス全体の気分サマリーに集約。
4. **アラート**（3つのルール）:
   - `sustained_negative_mood`——直近の観測で子どもが継続的に sad／angry を示す（継続に応じて warning → critical に深刻化）；
   - `teacher_negative_spike`——先生が一瞬怒り／ストレスを見せる（それ自体が安全シグナル）；
   - `sudden_mood_swing`——数分以内に happy → angry（要注意フラグ）。
5. **レポート**——コンソールダッシュボード、`classroom_report.json`、1ページの `report.html`。

## アーキテクチャ

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

## クイックスタート

```bash
pip install -r requirements.txt

# シミュレーション登園日デモを実行（子ども 8 名＋先生 1 名、台本あり）
python examples/demo.py
# -> コンソールダッシュボード + examples/output/classroom_report.json + report.html

# テストスイートを実行
python -m pytest tests/ -q
```

デモのストーリーは台本化されており、各ルールが目に見えて発火します：Child-04 は午後に不調に陥り（critical）、Teacher-01 は一度怒りを見せ（warning）、Child-02 は 20 分以内に happy→angry へ変化します（watch）。

## 実モデルへの差し替え

`EmotionClassifier` はプロトコルです——`classify(face_image) -> EmotionResult` を実装して差し込むだけ。`classifier.FERClassifier` に統合パスを文書化しています（`fer` または `deepface`、7 感情 → 4 クラスのマッピング付き）。実結果では `simulated=False` を維持し、下流のコードが区別できるようにしてください。

## 倫理とプライバシー

- **デモに実在の子どもの画像はゼロ。**全フレームが合成であり、"人物"はすべて生成された ID です。
- **想定用途は厳密にオプトイン**：実際の幼稚園への導入には、保護者の書面同意、公開されたデータ保持ポリシー、オンプレミス処理（子どもの顔のクラウドアップロードなし）、すべてのアラートの人間によるレビューが必要です——システムは*声かけを提案*するだけで、懲戒判断は決して行いません。
- 感情 AI には年齢・民族をまたぐ既知の精度とバイアスの限界があります。すべての出力を ground truth ではなく弱いシグナルとして扱ってください。

## ロードマップ

- [ ] `fer`／DeepFace の実分類器を組み込み、公開 FER データセットでベンチマーク
- [ ] 眠気／不注意シグナルを追加特徴として
- [ ] オンデバイスパッケージング（Jetson／Raspberry Pi）で教室展開
- [ ] アラート配信（SMS／職員アプリのプッシュ）、クワイエットアワー付き
- [ ] 子ども別の長期的な気分トレンド（プライバシー保護された集計のみ）

## ライセンス

MIT —— [LICENSE](LICENSE) を参照。
