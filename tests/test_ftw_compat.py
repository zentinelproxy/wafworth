"""Tests for go-ftw import compatibility."""

import tempfile
from pathlib import Path

import yaml

from wafplaybook.compat.ftw import _rule_id_to_category, import_ftw_file


def test_rule_id_mapping():
    assert _rule_id_to_category(942100) == "SQL Injection"
    assert _rule_id_to_category(941100) == "XSS"
    assert _rule_id_to_category(932100) == "Command Injection"
    assert _rule_id_to_category(930100) == "Path Traversal"
    assert _rule_id_to_category(920100) == "Protocol"
    assert _rule_id_to_category(913100) == "Scanner Detection"
    assert _rule_id_to_category(999999) == "Other"


def test_import_ftw_file():
    ftw_data = {
        "meta": {"author": "test", "enabled": True, "name": "942100.yaml"},
        "tests": [
            {
                "test_id": 942100,
                "desc": "SQL Injection test",
                "stages": [
                    {
                        "stage": {
                            "input": {
                                "method": "GET",
                                "uri": "/test?id=1' OR 1=1--",
                                "headers": {"Host": "localhost"},
                            },
                            "output": {"status": [403]},
                        }
                    }
                ],
            }
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(ftw_data, f)
        path = Path(f.name)

    tests = import_ftw_file(path)
    path.unlink()

    assert len(tests) == 1
    tc = tests[0]
    assert tc.id == "crs-942100-001"
    assert "sql-injection" in tc.tags
    assert "crs" in tc.tags
    assert tc.expected.action.value == "block"
    assert tc.request.path == "/test"
    assert "id=1' OR 1=1--" in tc.request.query_string


def test_import_ftw_file_allow():
    ftw_data = {
        "tests": [
            {
                "test_id": 920100,
                "desc": "Protocol allow test",
                "stages": [
                    {
                        "stage": {
                            "input": {
                                "method": "GET",
                                "uri": "/",
                            },
                            "output": {"status": [200]},
                        }
                    }
                ],
            }
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(ftw_data, f)
        path = Path(f.name)

    tests = import_ftw_file(path)
    path.unlink()

    assert len(tests) == 1
    assert tests[0].expected.action.value == "allow"


def test_import_empty_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"not_tests": True}, f)
        path = Path(f.name)

    tests = import_ftw_file(path)
    path.unlink()

    assert len(tests) == 0
