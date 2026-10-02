# Emotion-Guard

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | **[Español](README.es.md)** | [Português](README.pt.md) | [Русский](README.ru.md)

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Status: demo](https://img.shields.io/badge/status-demo_v0.1-orange)


**Monitoreo de emociones en aulas de jardín infantil para la seguridad — detectar el malestar antes de que escale.**

Emotion-Guard observa el ambiente del aula con señales faciales de emoción (alegría / calma / tristeza / enojo) en niños y docentes, lo agrega en un panel en vivo y emite alertas tempranas — p. ej. un niño que cae en un malestar sostenido o un docente con picos de estrés — para que el personal haga un seguimiento afectuoso *antes* de que la situación se convierta en un incidente.

> **Estado del proyecto: demo v0.1 (edición honesta).**
> El pipeline completo funciona hoy con datos **totalmente sintéticos**: fotogramas ficticios, un clasificador de emociones simulado con semilla fija y un escenario de aula guionizado. Sin niños reales, sin imágenes reales, sin pesos reales de modelo. Lo que es real: la base de detección de rostros (OpenCV Haar), la interfaz intercambiable del clasificador, las reglas de alerta y los informes. Lo que sigue siendo TODO (marcado claramente): integrar un modelo real de emociones (`fer` / DeepFace) y el despliegue en el dispositivo. Nada aquí pretende estar listo para producción.

## Contexto

Este proyecto nació de un trabajo real: un sistema de reconocimiento de emociones desplegado en jardines infantiles para detectar si los niños (y docentes) estaban felices, marcando el ánimo negativo sostenido como indicador temprano para ayudar a prevenir el maltrato y los incidentes violentos. Emotion-Guard es una reconstrucción demo *clean-room* de esa idea: la misma misión, datos sintéticos, lista para el portafolio.

## Qué hace

1. **Detección** de rostros en los fotogramas del aula (cascada Haar de OpenCV; detector simulado en la demo).
2. **Clasificación** de la emoción por rostro mediante una interfaz `EmotionClassifier` intercambiable (simulado determinista por defecto, etiquetado SIMULATED).
3. **Agregación** en resúmenes de ánimo por niño y de toda el aula.
4. **Alertas** con tres reglas:
   - `sustained_negative_mood`: un niño muestra tristeza/enojo en las observaciones más recientes (escala de warning → critical si persiste);
   - `teacher_negative_spike`: un docente muestra un destello de enojo/estrés (de por sí una señal de seguridad);
   - `sudden_mood_swing`: de alegría → enojo en minutos (bandera de observación).
5. **Informes**: panel en consola, `classroom_report.json` y un `report.html` de una página.

## Arquitectura

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

## Inicio rápido

```bash
pip install -r requirements.txt

# Ejecutar la demo simulada de un día escolar (8 niños + 1 docente, historia guionizada)
python examples/demo.py
# -> panel en consola + examples/output/classroom_report.json + report.html

# Ejecutar la suite de pruebas
python -m pytest tests/ -q
```

La historia de la demo está guionizada para que cada regla se dispare visiblemente: Child-04 cae en malestar por la tarde (critical), Teacher-01 muestra un destello de enojo (warning), Child-02 pasa de alegría → enojo en 20 minutos (watch).

## Integrar un modelo real

`EmotionClassifier` es un protocolo: implementa `classify(face_image) -> EmotionResult` e intégralo. `classifier.FERClassifier` documenta la ruta de integración (`fer` o `deepface`, con el mapeo de 7 emociones → 4 clases). Mantén `simulated=False` en resultados reales para que el código posterior los distinga.

## Ética y privacidad

- **La demo no contiene ninguna imagen real de niños.** Todos los fotogramas son sintéticos; todas las "personas" son IDs generados.
- **El uso previsto es estrictamente opt-in**: desplegarlo en un jardín real requiere consentimiento escrito de los padres, una política publicada de retención de datos, procesamiento local (sin subir rostros de niños a la nube) y revisión humana de cada alerta — el sistema *sugiere seguimientos*, nunca toma decisiones disciplinarias.
- La IA de emociones tiene limitaciones conocidas de precisión y sesgo según edades y etnias; trata cada salida como una señal débil, no como verdad absoluta.

## Hoja de ruta

- [ ] Integrar el clasificador real `fer` / DeepFace; benchmark en un dataset FER público
- [ ] Señales de somnolencia / falta de atención como features adicionales
- [ ] Empaquetado en dispositivo (Jetson / Raspberry Pi) para despliegue en aula
- [ ] Entrega de alertas (SMS / push a la app del personal) con política de horas silenciosas
- [ ] Tendencias de ánimo longitudinales por niño (solo agregados que preservan la privacidad)

## Licencia

MIT — ver [LICENSE](LICENSE).
