"""Multi-WAF result comparison."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table


def load_result(path: Path) -> dict:
    """Load a single result JSON file."""
    return json.loads(path.read_text())


def load_results(paths: list[str]) -> dict[str, dict]:
    """Load multiple result files/directories. Returns {name: data}."""
    results: dict[str, dict] = {}
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for f in sorted(path.glob("*.json")):
                data = load_result(f)
                name = data.get("meta", {}).get("target", f.stem)
                results[name] = data
        elif path.is_file() and path.suffix == ".json":
            data = load_result(path)
            name = data.get("meta", {}).get("target", path.stem)
            results[name] = data

    return results


def build_comparison(results: dict[str, dict]) -> dict:
    """Build a comparison structure from multiple result sets."""
    names = list(results.keys())
    all_categories: set[str] = set()
    for data in results.values():
        all_categories.update(data.get("by_category", {}).keys())

    comparison = {
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "targets": names,
            "categories": sorted(all_categories),
        },
        "overall": {},
        "by_category": {},
    }

    for name, data in results.items():
        comparison["overall"][name] = {
            "total_tests": data["meta"]["total_tests"],
            "passed": data["meta"]["passed"],
            "detection_rate": data["overall"]["detection_rate"],
            "false_positive_rate": data["overall"]["false_positive_rate"],
            "precision": data["overall"]["precision"],
            "f1": data["overall"]["f1"],
            "balanced_accuracy": data["overall"]["balanced_accuracy"],
            "latency": data.get("latency", {}),
        }

    for cat in sorted(all_categories):
        comparison["by_category"][cat] = {}
        for name, data in results.items():
            cat_data = data.get("by_category", {}).get(cat)
            if cat_data:
                comparison["by_category"][cat][name] = {
                    "detection_rate": cat_data["detection_rate"],
                    "false_positive_rate": cat_data["false_positive_rate"],
                    "confusion_matrix": cat_data["confusion_matrix"],
                }

    return comparison


def console_comparison(comparison: dict, console: Console | None = None) -> None:
    """Print comparison tables to console."""
    con = console or Console()
    targets = comparison["meta"]["targets"]

    # Overall table
    table = Table(title="WAF Comparison — Overall")
    table.add_column("Metric", style="bold")
    for name in targets:
        table.add_column(name, justify="right")

    for metric, label in [
        ("detection_rate", "Detection Rate"),
        ("false_positive_rate", "FP Rate"),
        ("precision", "Precision"),
        ("f1", "F1 Score"),
        ("balanced_accuracy", "Balanced Accuracy"),
    ]:
        row = [label]
        for name in targets:
            val = comparison["overall"].get(name, {}).get(metric, 0)
            row.append(f"{val:.1%}")
        table.add_row(*row)

    # Latency row
    row = ["Latency (p95)"]
    for name in targets:
        lat = comparison["overall"].get(name, {}).get("latency", {})
        p95 = lat.get("p95_ms", 0)
        row.append(f"{p95:.1f}ms")
    table.add_row(*row)

    con.print(table)

    # Per-category table
    cat_table = Table(title="WAF Comparison — Detection Rate by Category")
    cat_table.add_column("Category", style="bold")
    for name in targets:
        cat_table.add_column(name, justify="right")

    for cat in comparison["meta"]["categories"]:
        row = [cat]
        for name in targets:
            cat_data = comparison["by_category"].get(cat, {}).get(name)
            if cat_data:
                dr = cat_data["detection_rate"]
                style = "green" if dr >= 0.95 else "yellow" if dr >= 0.80 else "red"
                row.append(f"[{style}]{dr:.1%}[/{style}]")
            else:
                row.append("—")
        cat_table.add_row(*row)

    con.print(cat_table)


def json_comparison(comparison: dict, output_dir: str = ".") -> Path:
    """Write comparison to JSON."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "comparison.json"
    path.write_text(json.dumps(comparison, indent=2))
    return path


def markdown_comparison(comparison: dict, output_dir: str = ".") -> Path:
    """Write comparison to Markdown."""
    targets = comparison["meta"]["targets"]

    lines = [
        "# WAF Comparison",
        "",
        "## Overall Metrics",
        "",
        "| Metric | " + " | ".join(targets) + " |",
        "|--------| " + " | ".join("---:" for _ in targets) + " |",
    ]

    for metric, label in [
        ("detection_rate", "Detection Rate"),
        ("false_positive_rate", "FP Rate"),
        ("precision", "Precision"),
        ("f1", "F1 Score"),
        ("balanced_accuracy", "Balanced Accuracy"),
    ]:
        vals = []
        for name in targets:
            v = comparison["overall"].get(name, {}).get(metric, 0)
            vals.append(f"{v:.1%}")
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    lines.extend([
        "",
        "## Detection Rate by Category",
        "",
        "| Category | " + " | ".join(targets) + " |",
        "|----------| " + " | ".join("---:" for _ in targets) + " |",
    ])

    for cat in comparison["meta"]["categories"]:
        vals = []
        for name in targets:
            cat_data = comparison["by_category"].get(cat, {}).get(name)
            vals.append(f"{cat_data['detection_rate']:.1%}" if cat_data else "—")
        lines.append(f"| {cat} | " + " | ".join(vals) + " |")

    lines.append("")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "comparison.md"
    path.write_text("\n".join(lines))
    return path
