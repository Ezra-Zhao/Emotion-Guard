# Emotion-Guard

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | **[Português](README.pt.md)** | [Русский](README.ru.md)

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Status: demo](https://img.shields.io/badge/status-demo_v0.1-orange)


**Monitoramento de emoções em salas de aula de jardim de infância para a segurança — detectar o sofrimento antes que escale.**

O Emotion-Guard observa o clima da sala de aula por meio de sinais faciais de emoção (alegria / calma / tristeza / raiva) em crianças e professores, agrega tudo em um painel ao vivo e emite alertas precoces — p. ex. uma criança entrando em sofrimento prolongado ou um professor com picos de estresse — para que a equipe faça uma escuta acolhedora *antes* que a situação vire um incidente.

> **Estado do projeto: demo v0.1 (edição honesta).**
> O pipeline de ponta a ponta hoje roda com dados **totalmente sintéticos**: quadros fictícios, um classificador de emoções simulado com semente fixa e um cenário de sala de aula roteirizado. Sem crianças reais, sem imagens reais, sem pesos reais de modelo. O que é real: a base de detecção de rostos (OpenCV Haar), a interface trocável do classificador, as regras de alerta e os relatórios. O que ainda é TODO (marcado claramente): integrar um modelo real de emoções (`fer` / DeepFace) e a implantação no dispositivo. Nada aqui finge estar pronto para produção.

## Contexto

Este projeto nasceu de um trabalho real: um sistema de reconhecimento de emoções implantado em jardins de infância para detectar se as crianças (e professores) estavam felizes, sinalizando o humor negativo prolongado como indicador precoce para ajudar a prevenir maus-tratos e incidentes violentos. O Emotion-Guard é uma reconstrução demo *clean-room* dessa ideia — a mesma missão, dados sintéticos, pronta para o portfólio.

## O que faz

1. **Detecção** de rostos nos quadros da sala de aula (cascata Haar do OpenCV; detector simulado na demo).
2. **Classificação** da emoção por rosto por meio de uma interface `EmotionClassifier` trocável (simulado determinístico por padrão, rotulado SIMULATED).
3. **Agregação** em resumos de humor por criança e da sala inteira.
4. **Alertas** com três regras:
   - `sustained_negative_mood`: uma criança mostra tristeza/raiva nas observações mais recentes (escala de warning → critical se persistir);
   - `teacher_negative_spike`: um professor mostra um lampejo de raiva/estresse (por si só um sinal de segurança);
   - `sudden_mood_swing`: de alegria → raiva em minutos (bandeira de observação).
5. **Relatórios**: painel no console, `classroom_report.json` e um `report.html` de uma página.

## Arquitetura

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

## Início rápido

```bash
pip install -r requirements.txt

# Executar a demo simulada de um dia escolar (8 crianças + 1 professor, história roteirizada)
python examples/demo.py
# -> painel no console + examples/output/classroom_report.json + report.html

# Executar a suíte de testes
python -m pytest tests/ -q
```

A história da demo é roteirizada para que cada regra dispare visivelmente: Child-04 entra em sofrimento à tarde (critical), Teacher-01 mostra um lampejo de raiva (warning), Child-02 vai de alegria → raiva em 20 minutos (watch).

## Integrar um modelo real

`EmotionClassifier` é um protocolo — implemente `classify(face_image) -> EmotionResult` e encaixe. `classifier.FERClassifier` documenta o caminho de integração (`fer` ou `deepface`, com o mapeamento de 7 emoções → 4 classes). Mantenha `simulated=False` em resultados reais para que o código posterior os distinga.

## Ética e privacidade

- **A demo não contém nenhuma imagem real de crianças.** Todos os quadros são sintéticos; todas as "pessoas" são IDs gerados.
- **O uso pretendido é estritamente opt-in**: implantar em um jardim de infância real exige consentimento escrito dos pais, uma política publicada de retenção de dados, processamento local (sem upload de rostos de crianças para a nuvem) e revisão humana de cada alerta — o sistema *sugere escutas*, nunca toma decisões disciplinares.
- A IA de emoções tem limitações conhecidas de precisão e viés entre idades e etnias; trate cada saída como um sinal fraco, não como verdade absoluta.

## Roteiro

- [ ] Integrar o classificador real `fer` / DeepFace; benchmark em um dataset FER público
- [ ] Sinais de sonolência / desatenção como features adicionais
- [ ] Empacotamento no dispositivo (Jetson / Raspberry Pi) para implantação em sala de aula
- [ ] Entrega de alertas (SMS / push no app da equipe) com política de horário silencioso
- [ ] Tendências de humor longitudinais por criança (somente agregados que preservam a privacidade)

## Licença

MIT — ver [LICENSE](LICENSE).
