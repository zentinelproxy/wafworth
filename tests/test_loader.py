"""Tests for YAML loader."""

import tempfile
from pathlib import Path

import yaml

from wafworth.loader import filter_tests, load_test_dir, load_test_file, validate_test_files


def _write_yaml(tmp: Path, data: dict) -> Path:
    path = tmp / "test.yaml"
    path.write_text(yaml.dump(data, default_flow_style=False))
    return path


def _sample_data() -> dict:
    return {
        "meta": {
            "category": "SQL Injection",
            "subcategory": "Basic",
            "owasp": "A03",
            "severity": "critical",
        },
        "tests": [
            {
                "id": "sqli-001",
                "title": "OR 1=1",
                "tags": ["sqli", "basic", "paranoia-1"],
                "request": {
                    "method": "GET",
                    "path": "/api/users",
                    "query_string": "id=1' OR '1'='1",
                },
                "expected": {"status": 403, "action": "block"},
            },
            {
                "id": "sqli-002",
                "title": "UNION SELECT",
                "tags": ["sqli", "union", "paranoia-2"],
                "request": {
                    "method": "GET",
                    "path": "/api/users",
                    "query_string": "id=1 UNION SELECT * FROM users--",
                },
                "expected": {"status": 403, "action": "block"},
            },
        ],
    }


def test_load_test_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_yaml(Path(tmp), _sample_data())
        tf = load_test_file(path)
        assert tf.meta.category == "SQL Injection"
        assert len(tf.tests) == 2
        assert tf.tests[0].id == "sqli-001"
        assert tf.tests[0].meta is not None
        assert tf.tests[0].meta.category == "SQL Injection"


def test_load_test_dir():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subdir = root / "sqli"
        subdir.mkdir()
        _write_yaml(subdir, _sample_data())

        tests = load_test_dir(root)
        assert len(tests) == 2


def test_filter_tests_by_tag():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_yaml(Path(tmp), _sample_data())
        tf = load_test_file(path)

        filtered = filter_tests(tf.tests, tags=["union"])
        assert len(filtered) == 1
        assert filtered[0].id == "sqli-002"


def test_filter_tests_exclude_tag():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_yaml(Path(tmp), _sample_data())
        tf = load_test_file(path)

        filtered = filter_tests(tf.tests, exclude_tags=["paranoia-2"])
        assert len(filtered) == 1
        assert filtered[0].id == "sqli-001"


def test_filter_tests_by_severity():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_yaml(Path(tmp), _sample_data())
        tf = load_test_file(path)

        filtered = filter_tests(tf.tests, severity="critical")
        assert len(filtered) == 2

        filtered = filter_tests(tf.tests, severity="low")
        assert len(filtered) == 0


def test_validate_test_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_yaml(root, _sample_data())

        results = validate_test_files(root)
        assert len(results) == 1
        assert results[0][1] is None  # No error


def test_validate_invalid_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bad = root / "bad.yaml"
        bad.write_text("not_tests: true\n")

        results = validate_test_files(root)
        assert len(results) == 1
        assert results[0][1] is not None  # Has error
