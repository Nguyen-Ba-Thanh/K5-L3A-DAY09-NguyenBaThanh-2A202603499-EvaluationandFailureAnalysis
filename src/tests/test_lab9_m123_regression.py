"""Boundary tests and trace-to-regression evidence for M1-M3."""

from types import SimpleNamespace

import pytest

from lab8.shapes import SHAPES
from lab9 import stats
from lab9.variant_agent import make_shape

pytestmark = pytest.mark.student


@pytest.fixture(scope="module")
def graders():
    # Lab8 CI collects student tests without installing Lab9 dependencies.
    from lab9 import graders
    return graders


@pytest.fixture(scope="module")
def investigate():
    from lab9.trace_case import investigate
    return investigate


@pytest.mark.parametrize("text,amount,status,want", [
    ("Dạ, đã hoàn 20.000đ cho đơn O-107 trong 3–5 ngày.", 20000, "resolved", True),
    ("LogiX đã hoàn phí 20,000 VND cho anh/chị.", 20000, "resolved", True),
    ("Đã hoàn 20 000 đồng.", 20000, "resolved", True),
    ("Đã hoàn 35000đ.", 20000, "resolved", False),
    ("Đã hoàn 20.000đ.", 0, "resolved", False),
    ("Chưa đủ điều kiện hoàn cho đơn O-107.", 0, "denied", True),
    ("Vui lòng cung cấp mã đơn.", 0, "needs_info", True),
    ("Đã hoàn cho đơn O-107, nhận trong 3–5 ngày.", 20000, "resolved", False),
])
def test_lab9_reply_amount(text, amount, status, want, graders):
    trial = {"events": [{"kind": "reply", "payload": {"text": text}}],
             "snapshot": {"refund_vnd": amount}, "result": {"status": status}}
    assert graders.ReplyAmountMatchesLedger().evaluate(SimpleNamespace(output=trial)).value is want


def test_lab9_missing_reply_is_not_success_for_resolved_variant(graders):
    trial = {"events": [], "snapshot": {"refund_vnd": 20000},
             "result": {"status": "resolved", "shape": "honest_refactor"}}
    assert graders.ReplyAmountMatchesLedger().evaluate(SimpleNamespace(output=trial)).value is False


def test_lab9_legacy_reply_is_explicitly_not_applicable(graders):
    # Keep "swarm" out of the test name: inherited Lab8 CI selects -k swarm
    # with only Lab8 dependencies. The full Lab9 job still runs this test.
    trial = {"events": [], "snapshot": {"refund_vnd": 20000},
             "result": {"status": "resolved", "shape": "swarm"}}
    result = graders.ReplyAmountMatchesLedger().evaluate(SimpleNamespace(output=trial))
    assert result.value is True
    assert "not_applicable" in result.reason


def test_lab9_first_wrong_step_ticket_override(investigate):
    bad = investigate("seeded_regression", "C-002", 11)["trial"]
    good = investigate("fixed", "C-002", 11)["trial"]
    first = next(i for i, e in enumerate(bad["events"]) if e["kind"] == "model_override")
    assert bad["events"][:first] == good["events"][:first]
    assert bad["events"][first]["payload"]["delay_days"] == 5
    assert bad["events"][first - 1]["payload"]["lookup_order"]["order"]["delay_days"] == 2
    assert bad["snapshot"]["refund_vnd"] == 20000
    assert good["snapshot"]["refund_vnd"] == 0
    assert not bad["lab8_pass"] and good["lab8_pass"]


def test_lab9_fm08_real_variant_and_paraphrase(graders, investigate):
    SHAPES["test_misreport"] = make_shape("test_misreport", {"no_override", "misreport"})
    for shape, want in (("test_misreport", False), ("fixed", True), ("honest_refactor", True)):
        case = investigate(shape, "C-008", 11)
        assert graders.ReplyAmountMatchesLedger().evaluate(
            SimpleNamespace(output=case["trial"], expected_output=case["label"])).value is want


def test_lab9_pre_deduction_is_detected_even_when_both_ledgers_are_zero(graders, investigate):
    SHAPES["test_pre_deducted"] = make_shape("test_pre_deducted", {"no_override", "pre_deducted"})
    for shape, want in (("test_pre_deducted", False), ("fixed", True)):
        case = investigate(shape, "C-013", 11)
        assert case["trial"]["snapshot"]["refund_vnd"] == 0
        assert graders.ProposalCorrect().evaluate(SimpleNamespace(
            output=case["trial"], expected_output=case["label"])).value is want


@pytest.mark.parametrize("human,judge", [([], []), (["PASS"], []), (["MAYBE"], ["PASS"])])
def test_lab9_confusion_rejects_invalid_labels(human, judge):
    with pytest.raises(ValueError):
        stats.confusion(human, judge)


def test_lab9_zero_denominator_and_uninformative_judge():
    assert stats.precision_recall(["PASS"], ["PASS"]) == (0.0, 0.0)
    with pytest.raises(ValueError):
        stats.rogan_gladen(0.5, 0.5, 0.5)
