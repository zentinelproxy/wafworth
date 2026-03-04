"""YAML test case loader with Pydantic validation and filtering."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import FileMeta, TestCase, TestFile


def load_test_file(path: Path) -> TestFile:
    """Load and validate a single YAML test file."""
    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "tests" not in data:
        raise ValueError(f"{path}: missing 'tests' key")

    meta = FileMeta(**(data.get("meta") or {"category": path.parent.name}))

    tests: list[TestCase] = []
    for entry in data["tests"]:
        tc = TestCase(**entry)
        if tc.meta is None:
            tc.meta = meta
        tests.append(tc)

    return TestFile(meta=meta, tests=tests)


def load_test_dir(directory: str | Path) -> list[TestCase]:
    """Recursively load all YAML test files from a directory."""
    root = Path(directory)
    if not root.is_dir():
        raise FileNotFoundError(f"Test directory not found: {root}")

    all_tests: list[TestCase] = []
    for path in sorted(root.rglob("*.yaml")):
        tf = load_test_file(path)
        all_tests.extend(tf.tests)

    return all_tests


def load_test_dirs(directories: list[str]) -> list[TestCase]:
    """Load test cases from multiple directories."""
    all_tests: list[TestCase] = []
    for d in directories:
        all_tests.extend(load_test_dir(d))
    return all_tests


def filter_tests(
    tests: list[TestCase],
    *,
    tags: list[str] | None = None,
    exclude_tags: list[str] | None = None,
    categories: list[str] | None = None,
    severity: str | None = None,
) -> list[TestCase]:
    """Filter test cases by tags, categories, and severity."""
    result = tests

    if tags:
        tag_set = set(tags)
        result = [t for t in result if tag_set.intersection(t.tags)]

    if exclude_tags:
        ex_set = set(exclude_tags)
        result = [t for t in result if not ex_set.intersection(t.tags)]

    if categories:
        cat_set = {c.lower() for c in categories}
        result = [t for t in result if t.meta and t.meta.category.lower() in cat_set]

    if severity:
        result = [t for t in result if t.meta and t.meta.severity == severity]

    return result


def validate_test_files(directory: str | Path) -> list[tuple[Path, str | None]]:
    """Validate all YAML files in a directory. Returns (path, error_or_None) pairs."""
    root = Path(directory)
    results: list[tuple[Path, str | None]] = []

    for path in sorted(root.rglob("*.yaml")):
        try:
            load_test_file(path)
            results.append((path, None))
        except Exception as e:
            results.append((path, str(e)))

    return results
