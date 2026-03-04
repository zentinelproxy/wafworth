"""Confusion matrix computation and metric aggregation."""

from __future__ import annotations

import statistics
from collections import defaultdict

from .models import Action, ConfusionMatrix, Encoding, LatencyStats, TestResult


def compute_confusion_matrix(results: list[TestResult]) -> ConfusionMatrix:
    """Compute overall confusion matrix from test results."""
    cm = ConfusionMatrix()
    for r in results:
        if r.expected_action == Action.BLOCK:
            if r.passed:
                cm.tp += 1
            else:
                cm.fn += 1
        else:
            if r.passed:
                cm.tn += 1
            else:
                cm.fp += 1
    return cm


def compute_by_category(results: list[TestResult]) -> dict[str, ConfusionMatrix]:
    """Compute confusion matrix per category."""
    groups: dict[str, list[TestResult]] = defaultdict(list)
    for r in results:
        groups[r.category or "uncategorized"].append(r)
    return {cat: compute_confusion_matrix(rs) for cat, rs in sorted(groups.items())}


def compute_by_encoding(results: list[TestResult]) -> dict[Encoding, ConfusionMatrix]:
    """Compute confusion matrix per encoding."""
    groups: dict[Encoding, list[TestResult]] = defaultdict(list)
    for r in results:
        groups[r.encoding].append(r)
    return {enc: compute_confusion_matrix(rs) for enc, rs in sorted(groups.items(), key=lambda x: x[0].value)}


def compute_latency_stats(results: list[TestResult]) -> LatencyStats:
    """Compute latency percentiles from test results."""
    latencies = [r.latency_ms for r in results if r.error is None]
    if not latencies:
        return LatencyStats()

    latencies.sort()
    n = len(latencies)

    def percentile(p: float) -> float:
        idx = int(n * p / 100)
        return latencies[min(idx, n - 1)]

    return LatencyStats(
        p50_ms=round(percentile(50), 2),
        p95_ms=round(percentile(95), 2),
        p99_ms=round(percentile(99), 2),
        mean_ms=round(statistics.mean(latencies), 2),
        max_ms=round(max(latencies), 2),
    )


def failures(results: list[TestResult]) -> list[TestResult]:
    """Return only failed test results."""
    return [r for r in results if not r.passed]
