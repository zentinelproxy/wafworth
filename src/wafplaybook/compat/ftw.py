"""go-ftw (OWASP CRS) test file import compatibility."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..models import TestCase, TestExpected, TestRequest

# CRS rule ID ranges → waf-playbook categories
CRS_CATEGORY_MAP: dict[tuple[int, int], str] = {
    (901, 901): "Initialization",
    (910, 910): "Scanner Detection",
    (911, 911): "Protocol Enforcement",
    (912, 912): "Protocol Enforcement",
    (913, 913): "Scanner Detection",
    (920, 920): "Protocol",
    (921, 921): "Protocol",
    (930, 930): "Path Traversal",
    (931, 931): "Path Traversal",
    (932, 932): "Command Injection",
    (933, 933): "SSTI",
    (934, 934): "SSTI",
    (941, 941): "XSS",
    (942, 942): "SQL Injection",
    (943, 943): "Session Fixation",
    (944, 944): "Deserialization",
    (949, 949): "Blocking",
    (950, 950): "Data Leakage",
    (951, 951): "Data Leakage",
    (953, 953): "Data Leakage",
    (954, 954): "Data Leakage",
    (959, 959): "Blocking",
    (980, 980): "Correlation",
}


def _rule_id_to_category(rule_id: int) -> str:
    """Map a CRS rule ID to a waf-playbook category."""
    prefix = rule_id // 1000
    for (lo, hi), cat in CRS_CATEGORY_MAP.items():
        if lo <= prefix <= hi:
            return cat
    return "Other"


def _convert_ftw_test(
    rule_id: int,
    test_idx: int,
    stage: dict,
    meta_title: str = "",
) -> TestCase | None:
    """Convert a single go-ftw test stage to a TestCase."""
    inp = stage.get("input", {})
    out = stage.get("output", {})

    if not inp:
        return None

    method = inp.get("method", "GET")
    uri = inp.get("uri", "/")
    headers = inp.get("headers", {})
    data = inp.get("data", None)

    # go-ftw uses encoded_request or dest_addr sometimes — skip those
    if inp.get("encoded_request"):
        return None

    # Build query string from URI if present
    path = uri
    query_string = ""
    if "?" in uri:
        path, query_string = uri.split("?", 1)

    # Expected output
    expected_status = None
    action = "block"
    if "status" in out:
        status_list = out["status"]
        if isinstance(status_list, list):
            # go-ftw uses [403] or [200] etc
            expected_status = status_list[0] if status_list else 403
        else:
            expected_status = int(status_list)
        action = "allow" if expected_status == 200 else "block"
    elif out.get("no_log_contains") or out.get("expect_error", False):
        action = "allow"
        expected_status = 200

    category = _rule_id_to_category(rule_id)
    test_id = f"crs-{rule_id}-{test_idx:03d}"

    return TestCase(
        id=test_id,
        title=meta_title or f"CRS Rule {rule_id} test {test_idx}",
        tags=[category.lower().replace(" ", "-"), "crs", f"crs-{rule_id}"],
        request=TestRequest(
            method=method,
            path=path,
            query_string=query_string,
            headers={k: str(v) for k, v in headers.items()} if headers else {},
            body=data if isinstance(data, str) else None,
        ),
        expected=TestExpected(action=action, status=expected_status or (403 if action == "block" else 200)),
    )


def import_ftw_file(path: Path) -> list[TestCase]:
    """Import a go-ftw YAML test file into waf-playbook format."""
    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        return []

    tests_block = data.get("tests", [])
    if not isinstance(tests_block, list):
        return []

    results: list[TestCase] = []

    for test_entry in tests_block:
        rule_id = test_entry.get("test_id", test_entry.get("rule_id", 0))
        if isinstance(rule_id, str):
            try:
                rule_id = int(rule_id)
            except ValueError:
                continue

        desc = test_entry.get("desc", "")
        stages = test_entry.get("stages", [])

        for idx, stage_wrapper in enumerate(stages):
            stage = stage_wrapper.get("stage", stage_wrapper)
            tc = _convert_ftw_test(rule_id, idx + 1, stage, meta_title=desc)
            if tc:
                results.append(tc)

    return results


def import_ftw_dir(directory: Path) -> list[TestCase]:
    """Import all go-ftw YAML files from a directory."""
    results: list[TestCase] = []
    for path in sorted(directory.rglob("*.yaml")):
        results.extend(import_ftw_file(path))
    for path in sorted(directory.rglob("*.yml")):
        results.extend(import_ftw_file(path))
    return results


def export_to_yaml(tests: list[TestCase], output_dir: Path, category: str = "") -> list[Path]:
    """Export converted test cases to waf-playbook YAML format."""
    from collections import defaultdict

    by_category: dict[str, list[TestCase]] = defaultdict(list)
    for tc in tests:
        cat = tc.tags[0] if tc.tags else "other"
        by_category[cat].append(tc)

    written: list[Path] = []
    for cat, cat_tests in by_category.items():
        cat_dir = output_dir / cat.replace(" ", "-").lower()
        cat_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "meta": {
                "category": cat.replace("-", " ").title(),
                "subcategory": "CRS Import",
                "owasp": "",
                "severity": "high",
            },
            "tests": [
                {
                    "id": tc.id,
                    "title": tc.title,
                    "tags": tc.tags,
                    "request": {
                        "method": tc.request.method,
                        "path": tc.request.path,
                        **({"query_string": tc.request.query_string} if tc.request.query_string else {}),
                        **({"headers": tc.request.headers} if tc.request.headers else {}),
                        **({"body": tc.request.body} if tc.request.body else {}),
                    },
                    "expected": {
                        "status": tc.expected.status,
                        "action": tc.expected.action.value,
                    },
                }
                for tc in cat_tests
            ],
        }

        path = cat_dir / f"crs-{cat}.yaml"
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        written.append(path)

    return written
