"""Output reporters: Console (Rich), JSON, Markdown."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .metrics import (
    compute_by_category,
    compute_by_encoding,
    compute_confusion_matrix,
    compute_latency_stats,
    failures,
)
from .models import ConfusionMatrix, TestResult


def _cm_row(label: str, cm: ConfusionMatrix) -> list[str]:
    return [
        label,
        str(cm.tp),
        str(cm.fp),
        str(cm.tn),
        str(cm.fn),
        f"{cm.detection_rate:.1%}",
        f"{cm.false_positive_rate:.1%}",
        f"{cm.precision:.1%}",
        f"{cm.f1:.1%}",
    ]


class ConsoleReporter:
    """Rich console output."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    def report(self, results: list[TestResult], target_name: str = "") -> None:
        overall = compute_confusion_matrix(results)
        by_cat = compute_by_category(results)
        latency = compute_latency_stats(results)
        fails = failures(results)

        # Category table
        table = Table(title=f"WAF Test Results{f' — {target_name}' if target_name else ''}")
        for col in ["Category", "TP", "FP", "TN", "FN", "Detection", "FP Rate", "Precision", "F1"]:
            table.add_column(col, justify="right" if col != "Category" else "left")

        for cat, cm in by_cat.items():
            style = "green" if cm.detection_rate >= 0.95 else "yellow" if cm.detection_rate >= 0.80 else "red"
            table.add_row(*_cm_row(cat, cm), style=style)

        table.add_section()
        table.add_row(*_cm_row("TOTAL", overall), style="bold")
        self.console.print(table)

        # Latency
        self.console.print(
            f"\nLatency: p50={latency.p50_ms:.1f}ms  p95={latency.p95_ms:.1f}ms  "
            f"p99={latency.p99_ms:.1f}ms  mean={latency.mean_ms:.1f}ms  max={latency.max_ms:.1f}ms"
        )

        # Summary
        self.console.print(
            f"\n[bold]Total: {overall.total}  Passed: {overall.tp + overall.tn}  "
            f"Failed: {overall.fp + overall.fn}[/bold]"
        )
        self.console.print(
            f"Detection Rate: {overall.detection_rate:.1%}  FP Rate: {overall.false_positive_rate:.1%}  "
            f"Balanced Accuracy: {overall.balanced_accuracy:.1%}  Youden's J: {overall.youdens_index:.3f}"
        )

        # Top failures
        if fails:
            self.console.print(f"\n[bold red]Failures ({len(fails)}):[/bold red]")
            for f in fails[:20]:
                self.console.print(
                    f"  {f.test_id}: expected {f.expected_action.value} "
                    f"(status {f.expected_status}), got {f.actual_status} — {f.title}"
                )
            if len(fails) > 20:
                self.console.print(f"  ... and {len(fails) - 20} more")


class JSONReporter:
    """Machine-readable JSON output."""

    def report(self, results: list[TestResult], target_name: str = "", output_dir: str = ".") -> Path:
        overall = compute_confusion_matrix(results)
        by_cat = compute_by_category(results)
        by_enc = compute_by_encoding(results)
        latency = compute_latency_stats(results)
        fails = failures(results)

        data = {
            "meta": {
                "target": target_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_tests": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
            },
            "overall": {
                "confusion_matrix": overall.model_dump(),
                "detection_rate": overall.detection_rate,
                "false_positive_rate": overall.false_positive_rate,
                "precision": overall.precision,
                "f1": overall.f1,
                "balanced_accuracy": overall.balanced_accuracy,
                "youdens_index": overall.youdens_index,
            },
            "latency": latency.model_dump(),
            "by_category": {
                cat: {
                    "confusion_matrix": cm.model_dump(),
                    "detection_rate": cm.detection_rate,
                    "false_positive_rate": cm.false_positive_rate,
                }
                for cat, cm in by_cat.items()
            },
            "by_encoding": {
                enc.value: {
                    "confusion_matrix": cm.model_dump(),
                    "detection_rate": cm.detection_rate,
                }
                for enc, cm in by_enc.items()
            },
            "failures": [
                {
                    "test_id": f.test_id,
                    "expected_action": f.expected_action.value,
                    "expected_status": f.expected_status,
                    "actual_status": f.actual_status,
                    "encoding": f.encoding.value,
                    "category": f.category,
                    "title": f.title,
                    "error": f.error,
                }
                for f in fails
            ],
        }

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        import re
        name = re.sub(r"[^a-zA-Z0-9_-]", "-", target_name).strip("-").lower() or "results"
        path = out / f"{name}.json"
        path.write_text(json.dumps(data, indent=2))
        return path


class MarkdownReporter:
    """Markdown summary report."""

    def report(self, results: list[TestResult], target_name: str = "", output_dir: str = ".") -> Path:
        overall = compute_confusion_matrix(results)
        by_cat = compute_by_category(results)
        latency = compute_latency_stats(results)
        fails = failures(results)

        lines = [
            f"# WAF Test Results{f' — {target_name}' if target_name else ''}",
            "",
            f"**Total**: {overall.total} | **Passed**: {overall.tp + overall.tn} | "
            f"**Failed**: {overall.fp + overall.fn}",
            "",
            "## Overall Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Detection Rate | {overall.detection_rate:.1%} |",
            f"| False Positive Rate | {overall.false_positive_rate:.1%} |",
            f"| Precision | {overall.precision:.1%} |",
            f"| F1 Score | {overall.f1:.1%} |",
            f"| Balanced Accuracy | {overall.balanced_accuracy:.1%} |",
            f"| Youden's J | {overall.youdens_index:.3f} |",
            "",
            "## Latency",
            "",
            f"p50={latency.p50_ms:.1f}ms | p95={latency.p95_ms:.1f}ms | "
            f"p99={latency.p99_ms:.1f}ms | mean={latency.mean_ms:.1f}ms",
            "",
            "## Per-Category Breakdown",
            "",
            "| Category | TP | FP | TN | FN | Detection | FP Rate |",
            "|----------|---:|---:|---:|---:|----------:|--------:|",
        ]

        for cat, cm in by_cat.items():
            lines.append(
                f"| {cat} | {cm.tp} | {cm.fp} | {cm.tn} | {cm.fn} | "
                f"{cm.detection_rate:.1%} | {cm.false_positive_rate:.1%} |"
            )

        if fails:
            lines.extend([
                "",
                f"## Failures ({len(fails)})",
                "",
            ])
            for f in fails[:50]:
                lines.append(
                    f"- **{f.test_id}**: expected {f.expected_action.value} "
                    f"(status {f.expected_status}), got {f.actual_status} — {f.title}"
                )
            if len(fails) > 50:
                lines.append(f"- ... and {len(fails) - 50} more")

        lines.append("")

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        import re
        name = re.sub(r"[^a-zA-Z0-9_-]", "-", target_name).strip("-").lower() or "results"
        path = out / f"{name}-summary.md"
        path.write_text("\n".join(lines))
        return path
