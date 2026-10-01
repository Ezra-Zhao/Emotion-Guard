"""End-to-end demo: simulate classroom -> classify -> alerts -> reports.

Run from the repo root:

    python examples/demo.py [--seed 7] [--out examples/output]
"""

from __future__ import annotations

import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)  # for `import simulate`
sys.path.insert(0, os.path.dirname(_HERE))  # for `import emotion_guard`

from simulate import generate_classroom  # noqa: E402

from emotion_guard import (  # noqa: E402
    AlertConfig,
    AlertEngine,
    build_report,
    render_console,
    write_html,
    write_json,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Emotion-Guard simulated demo")
    ap.add_argument("--seed", type=int, default=7, help="Scenario master seed")
    ap.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"),
        help="Directory for classroom_report.json and report.html",
    )
    args = ap.parse_args()

    session = generate_classroom(master_seed=args.seed)

    # Stream the day slot-by-slot, evaluating after each batch of
    # observations -- the way a live classroom deployment would.
    # (Evaluating only once at end-of-day would miss mid-day spikes.)
    from emotion_guard import ClassroomSession  # noqa: E402

    live = ClassroomSession(name=session.name)
    for p in session.persons.values():
        live.add_person(p)
    engine = AlertEngine(AlertConfig())
    alerts = {pid: [] for pid in live.persons}
    seen = set()
    ordered = sorted(session.observations, key=lambda o: o.timestamp)
    slots = sorted({o.timestamp for o in ordered})
    for ts in slots:
        for o in ordered:
            if o.timestamp == ts:
                live.ingest(o)
        for pid in live.persons:
            for a in engine.evaluate(live.history(pid)):
                key = (a.person.person_id, a.rule, a.timestamp)
                if key not in seen:
                    seen.add(key)
                    alerts[pid].append(a)
    # Deterministic alert ordering for the report.
    for pid in alerts:
        alerts[pid].sort(key=lambda a: a.timestamp)

    print(render_console(live, alerts))

    report = build_report(live, alerts)
    os.makedirs(args.out, exist_ok=True)
    json_path = os.path.join(args.out, "classroom_report.json")
    html_path = os.path.join(args.out, "report.html")
    write_json(report, json_path)
    write_html(report, html_path)
    print(f"\nWrote:\n  {json_path}\n  {html_path}")


if __name__ == "__main__":
    main()
