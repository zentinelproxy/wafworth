"""Async HTTP executor using httpx with HTTP/2 and concurrency control."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable

import httpx

from .models import Action, ExpandedTestCase, TargetConfig, TestResult


async def execute_test(
    client: httpx.AsyncClient,
    target: TargetConfig,
    expanded: ExpandedTestCase,
    timeout: float = 10.0,
) -> TestResult:
    """Execute a single test case against the target."""
    req = expanded.effective_request
    tc = expanded.test_case

    url = target.base_url.rstrip("/") + req.path
    if req.query_string:
        url = f"{url}?{req.query_string}"

    headers = dict(req.headers)
    if req.content_type:
        headers["Content-Type"] = req.content_type

    start = time.monotonic()
    try:
        response = await client.request(
            method=req.method,
            url=url,
            headers=headers,
            content=req.body.encode() if req.body else None,
            timeout=timeout,
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        actual_status = response.status_code
        error = None
    except httpx.TimeoutException:
        elapsed_ms = (time.monotonic() - start) * 1000
        actual_status = 0
        error = "timeout"
    except httpx.HTTPError as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        actual_status = 0
        error = str(e)
    except Exception as e:
        # Catch invalid URLs from malicious test payloads (e.g. Host header injection)
        elapsed_ms = (time.monotonic() - start) * 1000
        actual_status = 0
        error = f"invalid_request: {e}"

    # Determine pass/fail
    expected_action = tc.expected.action
    if expected_action == Action.BLOCK:
        passed = target.is_block_status(actual_status)
    else:
        passed = target.is_allow_status(actual_status)

    return TestResult(
        test_id=expanded.effective_id,
        passed=passed,
        expected_action=expected_action,
        expected_status=tc.expected.status,
        actual_status=actual_status,
        latency_ms=elapsed_ms,
        encoding=expanded.encoding,
        category=tc.meta.category if tc.meta else "",
        title=tc.title,
        error=error,
    )


async def execute_all(
    target: TargetConfig,
    tests: list[ExpandedTestCase],
    concurrency: int = 10,
    timeout: float = 10.0,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[TestResult]:
    """Execute all test cases with concurrency control."""
    semaphore = asyncio.Semaphore(concurrency)
    results: list[TestResult] = []
    completed = 0
    total = len(tests)
    lock = asyncio.Lock()

    async with httpx.AsyncClient(http2=True, verify=False, follow_redirects=False) as client:

        async def run_one(expanded: ExpandedTestCase) -> TestResult:
            nonlocal completed
            async with semaphore:
                result = await execute_test(client, target, expanded, timeout)
            async with lock:
                completed += 1
                if on_progress:
                    on_progress(completed, total)
            return result

        tasks = [asyncio.create_task(run_one(t)) for t in tests]
        results = await asyncio.gather(*tasks)

    return list(results)
