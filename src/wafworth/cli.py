"""Click CLI for wafworth."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from . import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """WAF-agnostic testing framework with encoding auto-generation."""


@cli.command()
@click.option("--target", "-t", required=True, help="Target WAF URL (e.g. http://localhost:8080)")
@click.option("--name", "-n", default="", help="Target name for reports")
@click.option("--block-status", default=403, type=int, help="HTTP status code indicating a block")
@click.option("--testcases", "-d", multiple=True, default=["testcases"], help="Test case directories")
@click.option("--tags", help="Comma-separated tags to include")
@click.option("--exclude-tags", help="Comma-separated tags to exclude")
@click.option(
    "--encodings",
    default="plain",
    help="Comma-separated encodings (plain,url,double_url,hex,unicode_escape,html_entity,base64,utf7,overlong_utf8)",
)
@click.option("--concurrency", "-c", default=10, type=int, help="Max concurrent requests")
@click.option("--timeout", default=10.0, type=float, help="Per-request timeout in seconds")
@click.option("--output", "-o", default="results", help="Output directory for reports")
@click.option("--format", "fmt", type=click.Choice(["all", "console", "json", "markdown"]), default="all")
@click.option("--fail-under", type=float, help="Fail if detection rate below this threshold (e.g. 0.95)")
@click.option("--fail-fp-over", type=float, help="Fail if FP rate above this threshold (e.g. 0.05)")
def run(
    target: str,
    name: str,
    block_status: int,
    testcases: tuple[str, ...],
    tags: str | None,
    exclude_tags: str | None,
    encodings: str,
    concurrency: int,
    timeout: float,
    output: str,
    fmt: str,
    fail_under: float | None,
    fail_fp_over: float | None,
) -> None:
    """Run test cases against a WAF target."""
    from .encoder import expand_all
    from .executor import execute_all
    from .loader import filter_tests, load_test_dirs
    from .metrics import compute_confusion_matrix
    from .models import Encoding, TargetConfig
    from .reporter import ConsoleReporter, JSONReporter, MarkdownReporter

    target_config = TargetConfig(
        base_url=target,
        name=name or target,
        block_status=block_status,
    )

    # Load and filter
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    ex_tag_list = [t.strip() for t in exclude_tags.split(",")] if exclude_tags else None
    enc_list = [Encoding(e.strip()) for e in encodings.split(",")]

    with console.status("Loading test cases..."):
        all_tests = load_test_dirs(list(testcases))
        filtered = filter_tests(all_tests, tags=tag_list, exclude_tags=ex_tag_list)
        expanded = expand_all(filtered, enc_list)

    console.print(
        f"Loaded {len(all_tests)} tests, filtered to {len(filtered)}, "
        f"expanded to {len(expanded)} with encodings: {', '.join(e.value for e in enc_list)}"
    )

    # Execute
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Running tests...", total=len(expanded))

        def on_progress(done: int, total: int) -> None:
            progress.update(task, completed=done)

        results = asyncio.run(
            execute_all(target_config, expanded, concurrency=concurrency, timeout=timeout, on_progress=on_progress)
        )

    # Report
    if fmt in ("all", "console"):
        ConsoleReporter(console).report(results, target_name=target_config.name)

    if fmt in ("all", "json"):
        path = JSONReporter().report(results, target_name=target_config.name, output_dir=output)
        console.print(f"\nJSON results: {path}")

    if fmt in ("all", "markdown"):
        path = MarkdownReporter().report(results, target_name=target_config.name, output_dir=output)
        console.print(f"Markdown summary: {path}")

    # CI thresholds
    overall = compute_confusion_matrix(results)
    exit_code = 0

    if fail_under is not None and overall.detection_rate < fail_under:
        console.print(
            f"\n[red]FAIL: Detection rate {overall.detection_rate:.1%} "
            f"is below threshold {fail_under:.1%}[/red]"
        )
        exit_code = 1

    if fail_fp_over is not None and overall.false_positive_rate > fail_fp_over:
        console.print(
            f"\n[red]FAIL: FP rate {overall.false_positive_rate:.1%} "
            f"is above threshold {fail_fp_over:.1%}[/red]"
        )
        exit_code = 1

    if exit_code:
        sys.exit(exit_code)


@cli.command()
@click.option("--results", "-r", multiple=True, required=True, help="Result JSON files or directories")
@click.option("--output", "-o", default="results/comparison", help="Output directory")
@click.option("--format", "fmt", type=click.Choice(["all", "console", "json", "markdown"]), default="all")
def compare(results: tuple[str, ...], output: str, fmt: str) -> None:
    """Compare results from multiple WAF targets."""
    from .comparator import (
        build_comparison,
        console_comparison,
        json_comparison,
        load_results,
        markdown_comparison,
    )

    data = load_results(list(results))
    if len(data) < 2:
        console.print("[red]Need at least 2 result sets to compare[/red]")
        sys.exit(1)

    comparison = build_comparison(data)

    if fmt in ("all", "console"):
        console_comparison(comparison, console)

    if fmt in ("all", "json"):
        path = json_comparison(comparison, output)
        console.print(f"\nComparison JSON: {path}")

    if fmt in ("all", "markdown"):
        path = markdown_comparison(comparison, output)
        console.print(f"Comparison Markdown: {path}")


@cli.command("list")
@click.option("--testcases", "-d", multiple=True, default=["testcases"], help="Test case directories")
@click.option("--tags", help="Comma-separated tags to filter")
@click.option("--severity", help="Filter by severity (critical, high, medium, low, info)")
@click.option("--categories", help="Comma-separated categories to filter")
def list_tests(testcases: tuple[str, ...], tags: str | None, severity: str | None, categories: str | None) -> None:
    """List available test cases with filtering."""
    from collections import Counter

    from rich.table import Table

    from .loader import filter_tests, load_test_dirs

    all_tests = load_test_dirs(list(testcases))
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    cat_list = [c.strip() for c in categories.split(",")] if categories else None
    filtered = filter_tests(all_tests, tags=tag_list, severity=severity, categories=cat_list)

    # Summary by category
    cat_counts: Counter[str] = Counter()
    for t in filtered:
        cat_counts[t.meta.category if t.meta else "uncategorized"] += 1

    table = Table(title=f"Test Cases ({len(filtered)} total)")
    table.add_column("Category")
    table.add_column("Count", justify="right")

    for cat, count in sorted(cat_counts.items()):
        table.add_row(cat, str(count))

    console.print(table)

    # Tag summary
    tag_counts: Counter[str] = Counter()
    for t in filtered:
        for tag in t.tags:
            tag_counts[tag] += 1

    console.print(f"\nTop tags: {', '.join(f'{t}({c})' for t, c in tag_counts.most_common(15))}")


@cli.command()
@click.argument("directories", nargs=-1, required=True)
def validate(directories: tuple[str, ...]) -> None:
    """Validate YAML test case files."""
    from .loader import validate_test_files

    total = 0
    errors = 0

    for d in directories:
        results = validate_test_files(d)
        for path, error in results:
            total += 1
            if error:
                errors += 1
                console.print(f"[red]FAIL[/red] {path}: {error}")
            else:
                console.print(f"[green]OK[/green]   {path}")

    console.print(f"\n{total} files checked, {total - errors} valid, {errors} errors")
    if errors:
        sys.exit(1)


@cli.command()
@click.argument("payload")
def encode(payload: str) -> None:
    """Encode a payload with all supported encodings."""
    from rich.table import Table

    from .encoder import ENCODERS

    table = Table(title=f"Encodings for: {payload}")
    table.add_column("Encoding")
    table.add_column("Result")

    table.add_row("plain", payload)
    for enc, func in ENCODERS.items():
        try:
            result = func(payload)
            table.add_row(enc.value, result)
        except Exception as e:
            table.add_row(enc.value, f"[red]Error: {e}[/red]")

    console.print(table)


@cli.group("import")
def import_group() -> None:
    """Import test cases from external formats."""


@import_group.command("ftw")
@click.argument("source", type=click.Path(exists=True))
@click.option("--output", "-o", default="testcases", help="Output directory for converted tests")
def import_ftw(source: str, output: str) -> None:
    """Import go-ftw (OWASP CRS) test files."""
    from .compat.ftw import export_to_yaml, import_ftw_dir, import_ftw_file

    source_path = Path(source)
    if source_path.is_file():
        tests = import_ftw_file(source_path)
    else:
        tests = import_ftw_dir(source_path)

    if not tests:
        console.print("[yellow]No tests found in the source[/yellow]")
        return

    console.print(f"Imported {len(tests)} tests from go-ftw format")

    written = export_to_yaml(tests, Path(output))
    for p in written:
        console.print(f"  Written: {p}")

    console.print(f"\n{len(written)} files written to {output}/")
