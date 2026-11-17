"""Additional M4-M7 checks for plausible reports, not variant-name matching."""

import copy
import json

import pytest

from lab9 import gate, stats

pytestmark = pytest.mark.student
SPEC = {"eval_set_version": "v2", "metrics": [
    {"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.8}}],
    "slices": [{"name": "money_movement", "metric": "pass_rate", "min": 0.8,
                "blocking": True, "no_significant_drop": True}]}


def report():
    return {"manifest": {"items": 2, "seeds": [11, 22], "eval_set_sha": "same"},
            "rows": [{"item_id": f"E-{i}", "seed": s, "pass_rate": True,
                      "cost": 1, "slices": ["money_movement"]} for i in range(2) for s in (11, 22)],
            "metrics": {"pass_rate": 1.0}, "evaluator_failures": []}


@pytest.mark.parametrize("attack", ["duplicate", "null_score", "failures_on_green", "retag",
                                   "cherry_pick", "edited_summary", "inf", "null_metric"])
def test_lab9_integrity_rejects_gamed_report(attack):
    base, pr = report(), report()
    if attack == "duplicate":
        pr["rows"][-1] = copy.deepcopy(pr["rows"][0])
    elif attack == "null_score":
        pr["rows"][0]["pass_rate"] = None
    elif attack == "failures_on_green":
        pr["evaluator_failures"] = ["grader crashed, even though aggregate looks green"]
    elif attack == "retag":
        for row in pr["rows"]:
            row["slices"] = []
    elif attack == "cherry_pick":
        pr["manifest"]["seeds"] = [11]
        pr["rows"] = [row for row in pr["rows"] if row["seed"] == 11]
    elif attack == "edited_summary":
        pr["rows"][0]["pass_rate"] = False
    elif attack == "inf":
        pr["metrics"]["pass_rate"] = float("inf")
    elif attack == "null_metric":
        pr["metrics"]["pass_rate"] = None
    assert gate.integrity_check(pr, base, SPEC)
    assert gate.check(pr, base, SPEC)[0] == ["integrity"]


@pytest.mark.parametrize("attack", ["remove_metric", "disable", "remove_ci", "remove_slice", "lower_floor"])
def test_lab9_ratchet_preserves_existing_guards(attack):
    loose = copy.deepcopy(SPEC)
    if attack == "remove_metric":
        loose["metrics"] = []
    elif attack == "disable":
        loose["metrics"][0]["blocking"] = False
    elif attack == "remove_ci":
        del loose["slices"][0]["no_significant_drop"]
    elif attack == "remove_slice":
        loose["slices"] = []
    elif attack == "lower_floor":
        loose["metrics"][0]["threshold"]["min"] = 0.7
    assert gate.integrity_check(report(), report(), loose, SPEC)


def test_lab9_self_comparison_and_tighter_spec_are_valid():
    tight = copy.deepcopy(SPEC)
    tight["metrics"][0]["threshold"]["min"] = 0.9
    assert gate.check(report(), report(), tight, SPEC)[0] == []


@pytest.mark.parametrize("args", [(0, 0, 1), (5, -1, 1), (5, 6, 1), (5, 2, 0),
                                  (3, 1, 4), (5.0, 2, 1), (True, 0, 1)])
def test_lab9_pass_k_checks_domain(args):
    for fn in (stats.pass_at_k, stats.pass_hat_k):
        with pytest.raises(ValueError):
            fn(*args)


def test_lab9_pass_k_orders_success_and_reliability():
    assert stats.pass_hat_k(5, 4, 5) == 0
    assert stats.pass_at_k(5, 4, 5) == 1
    assert stats.pass_hat_k(5, 4, 3) <= stats.pass_at_k(5, 4, 1) <= stats.pass_at_k(5, 4, 3)


def test_lab9_bootstrap_rejects_unpaired_or_nan():
    for a, b in (([], []), ([1], [1, 2]), ([float("nan")], [0])):
        with pytest.raises(ValueError):
            stats.paired_bootstrap(a, b)


def test_lab9_evalset_writes_canonical_lf(tmp_path, monkeypatch):
    from lab9 import evalset
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "data/public_claims.jsonl"
    source.parent.mkdir()
    source.write_text(json.dumps({"claim_id": "C-001", "matrix_id": "T01",
                                 "expected": {"refund_vnd": 35000}}), encoding="utf-8")
    evalset.build(source)
    blob = evalset.ITEMS.read_bytes()
    assert b"\r\n" not in blob
    assert blob.endswith(b"\n")
