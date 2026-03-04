"""Tests for Pydantic models."""

from pytest import approx

from wafworth.models import (
    Action,
    ConfusionMatrix,
    TestCase,
    TestExpected,
    TestRequest,
)


def test_test_expected_block():
    exp = TestExpected(action="block", status=403)
    assert exp.block is True
    assert exp.action == Action.BLOCK


def test_test_expected_allow():
    exp = TestExpected(action="allow", status=200)
    assert exp.block is False
    assert exp.action == Action.ALLOW


def test_test_expected_legacy_status_only():
    """Backward compat: infer action from status when action is missing."""
    exp = TestExpected.model_validate({"status": 200})
    assert exp.action == Action.ALLOW
    assert exp.status == 200

    exp2 = TestExpected.model_validate({"status": 403})
    assert exp2.action == Action.BLOCK


def test_test_expected_defaults():
    """Default is block with status 403."""
    exp = TestExpected.model_validate({"action": "block"})
    assert exp.status == 403


def test_test_case_is_false_positive():
    tc = TestCase(
        id="fp-001",
        title="Test",
        request=TestRequest(),
        expected=TestExpected(action="allow", status=200),
    )
    assert tc.is_false_positive is True


def test_test_case_is_attack():
    tc = TestCase(
        id="sqli-001",
        title="Test",
        request=TestRequest(),
        expected=TestExpected(action="block", status=403),
    )
    assert tc.is_false_positive is False


def test_confusion_matrix_metrics():
    cm = ConfusionMatrix(tp=90, fp=5, tn=95, fn=10)

    assert cm.total == 200
    assert cm.detection_rate == 90 / 100  # 0.9
    assert cm.false_positive_rate == 5 / 100  # 0.05
    assert cm.precision == 90 / 95
    assert cm.recall == cm.detection_rate
    assert cm.f1 > 0

    # Balanced accuracy = (TPR + TNR) / 2
    tpr = 90 / 100
    tnr = 95 / 100
    assert cm.balanced_accuracy == (tpr + tnr) / 2

    # Youden's J = TPR - FPR
    assert cm.youdens_index == approx(tpr - 5 / 100)


def test_confusion_matrix_add():
    a = ConfusionMatrix(tp=10, fp=2, tn=8, fn=5)
    b = ConfusionMatrix(tp=5, fp=1, tn=4, fn=3)
    c = a + b
    assert c.tp == 15
    assert c.fp == 3
    assert c.tn == 12
    assert c.fn == 8


def test_confusion_matrix_empty():
    cm = ConfusionMatrix()
    assert cm.detection_rate == 0.0
    assert cm.false_positive_rate == 0.0
    assert cm.precision == 0.0
    assert cm.f1 == 0.0
