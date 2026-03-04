"""Tests for metrics computation."""

from wafplaybook.metrics import (
    compute_by_category,
    compute_by_encoding,
    compute_confusion_matrix,
    compute_latency_stats,
    failures,
)
from wafplaybook.models import Action, Encoding, TestResult


def _result(
    test_id: str,
    passed: bool,
    action: str = "block",
    status: int = 403,
    latency: float = 5.0,
    encoding: str = "plain",
    category: str = "SQL Injection",
) -> TestResult:
    return TestResult(
        test_id=test_id,
        passed=passed,
        expected_action=Action(action),
        expected_status=403 if action == "block" else 200,
        actual_status=status,
        latency_ms=latency,
        encoding=Encoding(encoding),
        category=category,
    )


def test_confusion_matrix_basic():
    results = [
        _result("t1", True, "block"),    # TP
        _result("t2", False, "block"),   # FN
        _result("t3", True, "allow"),    # TN
        _result("t4", False, "allow"),   # FP
    ]
    cm = compute_confusion_matrix(results)
    assert cm.tp == 1
    assert cm.fn == 1
    assert cm.tn == 1
    assert cm.fp == 1


def test_by_category():
    results = [
        _result("t1", True, "block", category="SQL Injection"),
        _result("t2", True, "block", category="XSS"),
        _result("t3", False, "block", category="SQL Injection"),
    ]
    by_cat = compute_by_category(results)
    assert "SQL Injection" in by_cat
    assert "XSS" in by_cat
    assert by_cat["SQL Injection"].tp == 1
    assert by_cat["SQL Injection"].fn == 1
    assert by_cat["XSS"].tp == 1


def test_by_encoding():
    results = [
        _result("t1", True, "block", encoding="plain"),
        _result("t2", True, "block", encoding="url"),
        _result("t3", False, "block", encoding="url"),
    ]
    by_enc = compute_by_encoding(results)
    assert Encoding.PLAIN in by_enc
    assert Encoding.URL in by_enc
    assert by_enc[Encoding.PLAIN].tp == 1
    assert by_enc[Encoding.URL].tp == 1
    assert by_enc[Encoding.URL].fn == 1


def test_latency_stats():
    results = [
        _result("t1", True, latency=10.0),
        _result("t2", True, latency=20.0),
        _result("t3", True, latency=30.0),
        _result("t4", True, latency=100.0),
    ]
    stats = compute_latency_stats(results)
    assert stats.mean_ms == 40.0
    assert stats.max_ms == 100.0
    assert stats.p50_ms > 0


def test_latency_stats_empty():
    stats = compute_latency_stats([])
    assert stats.mean_ms == 0.0


def test_failures():
    results = [
        _result("t1", True),
        _result("t2", False),
        _result("t3", False),
    ]
    fails = failures(results)
    assert len(fails) == 2
    assert all(not f.passed for f in fails)
