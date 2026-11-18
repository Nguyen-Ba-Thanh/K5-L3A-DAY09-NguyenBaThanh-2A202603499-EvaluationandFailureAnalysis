"""Reproduce M1-M3 evidence without editing agents or report JSON by hand.

Run from src/: python -m lab9.m123_evidence
Only safe event summaries are exported; leaky debug payloads stay excluded.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from lab8.shapes import SHAPES
from lab9 import evalset, judge
from lab9.graders import GRADERS, MONEY
import re
from lab9.trace_case import investigate
from lab9.variant_agent import make_shape


EXAMPLES = {
    "FM-01": ("leaky_trace", "C-010", 11),
    "FM-02": ("ignore_denied", "C-007", 11),
    "FM-03": ("ticket_trust", "C-002", 11),
    "FM-04": ("sum_parts", "C-014", 11),
    "FM-05": ("pre_deducted", "C-014", 11),
    "FM-06": ("stale_clause", "C-006", 11),
    "FM-07": ("sibling_refund", "C-010", 11),
    "FM-08": ("misreport", "C-008", 11),
}


def summarize(case):
    trial, label = case["trial"], case["label"]
    ctx = SimpleNamespace(output=trial, expected_output=label)
    events = []
    for index, event in enumerate(trial["events"], 1):
        payload = event.get("payload") or {}
        safe = {key: payload[key] for key in
                ("amount_vnd", "delay_days", "refunded_vnd", "refund_count", "status") if key in payload}
        if event["kind"] == "investigator":
            safe["db_delay_days"] = payload.get("lookup_order", {}).get("order", {}).get("delay_days")
        if event["kind"] == "reply":
            safe["reply_amounts"] = [int(re.sub(r"\D", "", m.group(1)))
                                     for m in MONEY.finditer(payload.get("text", ""))]
        # Never export the debug_claim_row payload: it deliberately contains secrets.
        events.append({"step": index, "kind": event["kind"], "facts": safe})
    return {
        "run_id": trial["result"]["run_id"],
        "status": trial["result"]["status"],
        "proposal_amount": trial["result"]["proposal_amount"],
        "snapshot": trial["snapshot"],
        "expected": {k: label[k] for k in ("status", "proposal_amount", "refund_vnd")},
        "unexpected_rows": trial["unexpected_rows"],
        "lab8_pass": trial["lab8_pass"],
        "lab8_reason": ("forbidden_substring:[redacted]" if str(trial["lab8_reason"]).startswith("forbidden_substring:")
                        else trial["lab8_reason"]),
        "graders": {name: {"value": bool(g().evaluate(ctx).value)} for name, g in GRADERS.items()},
        "events": events,
    }


def main():
    from lab9.eval import load_spec
    from lab9.mutation import detect

    calibration = {name: judge.calibrate(Path(f"data/eval/judge_{name}_public.csv"))
                   for name in ("tone", "helpful")}
    examples = {}
    for fm, (bug, claim, seed) in EXAMPLES.items():
        name = f"m1_{bug}"
        # Runtime registration of the provided factory, not a change to variants.py.
        SHAPES[name] = make_shape(name, {"no_override", bug})
        examples[fm] = {"bug": bug, "claim_id": claim, "seed": seed,
                        "broken": summarize(investigate(name, claim, seed)),
                        "fixed": summarize(investigate("fixed", claim, seed))}
    trace_case = {shape: summarize(investigate(shape, "C-002", 11))
                  for shape in ("seeded_regression", "fixed")}
    detection, false_alarms = detect(load_spec())
    report = {
        "generated_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
        "command": "python -m lab9.m123_evidence",
        "eval_set_sha": evalset.sha12(evalset.ITEMS),
        "calibration": calibration, "examples": examples, "trace_case": trace_case,
        "detection": detection, "false_alarms": false_alarms,
    }
    out = Path("reports/m123_evidence.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    for name, result in calibration.items():
        print(name, {k: result[k] for k in ("n", "kappa", "precision", "recall", "passed")})
    for fm, ex in examples.items():
        print(fm, ex["broken"]["lab8_pass"], ex["broken"]["lab8_reason"],
              "fixed:", ex["fixed"]["lab8_pass"])
    print("detection:", detection, "false alarms:", false_alarms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
