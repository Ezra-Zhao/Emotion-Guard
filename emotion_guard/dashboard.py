"""Report rendering: console dashboard, JSON, and a simple HTML page."""

from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Dict, List

from .schemas import Alert, Emotion, Person, Role
from .classroom import ClassroomSession

_EMOJI = {
    Emotion.HAPPY: "😊",
    Emotion.CALM: "😐",
    Emotion.SAD: "😟",
    Emotion.ANGRY: "😠",
}

_LEVEL_TAG = {"watch": "[WATCH]", "warning": "[WARNING]", "critical": "[CRITICAL]"}


def _bar(fraction: float, width: int = 20) -> str:
    filled = int(round(fraction * width))
    return "█" * filled + "░" * (width - filled)


def render_console(
    session: ClassroomSession, alerts: Dict[str, List[Alert]]
) -> str:
    lines = []
    lines.append("=" * 64)
    lines.append(f"  Emotion-Guard classroom dashboard — {session.name}")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("  NOTE: all data below is SIMULATED demo data.")
    lines.append("=" * 64)

    mood = session.classroom_mood()
    lines.append("\nClassroom mood (overall):")
    for e in Emotion:
        lines.append(
            f"  {_EMOJI[e]} {e.value:6s} {_bar(mood[e.value])} {mood[e.value]*100:5.1f}%"
        )

    lines.append("\nPer-person mood:")
    for pid, person in sorted(session.persons.items()):
        tag = "TEACHER" if person.role == Role.TEACHER else "child  "
        summary = session.mood_summary(pid)
        n = len(session.history(pid))
        dominant = max(Emotion, key=lambda e: summary[e.value])
        lines.append(
            f"  [{tag}] {person.name:10s} "
            f"dominant {_EMOJI[dominant]}{dominant.value:6s} "
            f"(n={n}) "
            + " ".join(f"{_EMOJI[e]}{summary[e.value]*100:4.0f}%" for e in Emotion)
        )

    lines.append("\nAlerts:")
    any_alerts = False
    for pid in sorted(alerts):
        for a in alerts[pid]:
            any_alerts = True
            lines.append(
                f"  {_LEVEL_TAG.get(a.level, '[?]')} {a.person.name} "
                f"({a.timestamp.strftime('%H:%M')}) — {a.message} [{a.rule}]"
            )
    if not any_alerts:
        lines.append("  (none — classroom mood is stable)")
    lines.append("=" * 64)
    return "\n".join(lines)


def build_report(
    session: ClassroomSession, alerts: Dict[str, List[Alert]]
) -> dict:
    persons = []
    for pid, person in sorted(session.persons.items()):
        persons.append(
            {
                "person_id": pid,
                "name": person.name,
                "role": person.role.value,
                "observations": len(session.history(pid)),
                "mood": session.mood_summary(pid),
                "alerts": [
                    {
                        "level": a.level,
                        "message": a.message,
                        "rule": a.rule,
                        "timestamp": a.timestamp.isoformat(),
                    }
                    for a in alerts.get(pid, [])
                ],
            }
        )
    return {
        "classroom": session.name,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "simulated": True,
        "classroom_mood": session.classroom_mood(),
        "persons": persons,
    }


def write_json(report: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def write_html(report: dict, path: str) -> None:
    def esc(s: str) -> str:
        return html.escape(s)

    rows = []
    for p in report["persons"]:
        mood_cells = " ".join(
            f"{_EMOJI[e]} {p['mood'][e.value]*100:.0f}%"
            for e in Emotion
        )
        alert_cells = (
            "<br>".join(
                f"<b>[{a['level']}]</b> {esc(a['message'])}"
                for a in p["alerts"]
            )
            or "<i>none</i>"
        )
        rows.append(
            f"<tr><td>{esc(p['name'])}</td><td>{p['role']}</td>"
            f"<td>{p['observations']}</td><td>{mood_cells}</td>"
            f"<td>{alert_cells}</td></tr>"
        )
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Emotion-Guard — {esc(report['classroom'])} (SIMULATED DEMO)</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #222; }}
.banner {{ background: #fff3cd; border: 1px solid #e0c36a; padding: 0.8rem 1rem;
           border-radius: 8px; margin-bottom: 1.5rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 0.5rem 0.7rem; text-align: left;
          vertical-align: top; }}
th {{ background: #f5f5f5; }}
</style></head><body>
<h1>Emotion-Guard — {esc(report['classroom'])}</h1>
<div class="banner"><b>Simulated demo data.</b> No real children were observed.
Generated {esc(report['generated_at'])}.</div>
<h2>Classroom mood</h2>
<p>{" ".join(f"{_EMOJI[e]} <b>{e.value}</b> {report['classroom_mood'][e.value]*100:.0f}%"
for e in Emotion)}</p>
<h2>Per-person summary</h2>
<table><tr><th>Name</th><th>Role</th><th>Obs.</th><th>Mood mix</th><th>Alerts</th></tr>
{"".join(rows)}
</table></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
