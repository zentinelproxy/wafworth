"""Pydantic v2 models for waf-playbook."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Action(str, Enum):
    BLOCK = "block"
    ALLOW = "allow"


class Encoding(str, Enum):
    PLAIN = "plain"
    URL = "url"
    DOUBLE_URL = "double_url"
    HEX = "hex"
    UNICODE_ESCAPE = "unicode_escape"
    HTML_ENTITY = "html_entity"
    BASE64 = "base64"
    UTF7 = "utf7"
    OVERLONG_UTF8 = "overlong_utf8"


class TestRequest(BaseModel):
    method: str = "GET"
    path: str = "/"
    query_string: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    body: str | None = None
    content_type: str | None = None


class TestExpected(BaseModel):
    action: Action = Action.BLOCK
    status: int | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Backward compat: infer action from status if action missing
            if "action" not in data and "status" in data:
                data = dict(data)
                data["action"] = "allow" if data["status"] == 200 else "block"
            # If action is present but not status, set a default status
            if "status" not in data:
                data = dict(data)
                data["status"] = 200 if data.get("action") == "allow" else 403
        return data

    @property
    def block(self) -> bool:
        return self.action == Action.BLOCK


class FileMeta(BaseModel):
    category: str
    subcategory: str = ""
    owasp: str = ""  # OWASP Top 10 (e.g. "A03") or WSTG ID (e.g. "WSTG-INPV-05")
    severity: str = "medium"


class TestCase(BaseModel):
    id: str
    title: str
    tags: list[str] = Field(default_factory=list)
    request: TestRequest
    expected: TestExpected
    meta: FileMeta | None = None

    @property
    def is_false_positive(self) -> bool:
        return self.expected.action == Action.ALLOW


class ExpandedTestCase(BaseModel):
    """A TestCase with a specific encoding applied."""

    test_case: TestCase
    encoding: Encoding = Encoding.PLAIN
    original_id: str = ""
    encoded_request: TestRequest | None = None

    @property
    def effective_id(self) -> str:
        if self.encoding == Encoding.PLAIN:
            return self.test_case.id
        return f"{self.test_case.id}:{self.encoding.value}"

    @property
    def effective_request(self) -> TestRequest:
        return self.encoded_request if self.encoded_request else self.test_case.request


class TestResult(BaseModel):
    test_id: str
    passed: bool
    expected_action: Action
    expected_status: int | None = None
    actual_status: int
    latency_ms: float
    encoding: Encoding = Encoding.PLAIN
    category: str = ""
    title: str = ""
    error: str | None = None


class ConfusionMatrix(BaseModel):
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def detection_rate(self) -> float:
        """Recall / True Positive Rate."""
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0

    @property
    def false_positive_rate(self) -> float:
        return self.fp / (self.fp + self.tn) if (self.fp + self.tn) > 0 else 0.0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0

    @property
    def recall(self) -> float:
        return self.detection_rate

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    @property
    def balanced_accuracy(self) -> float:
        tpr = self.detection_rate
        tnr = self.tn / (self.tn + self.fp) if (self.tn + self.fp) > 0 else 0.0
        return (tpr + tnr) / 2

    @property
    def youdens_index(self) -> float:
        return self.detection_rate + (1 - self.false_positive_rate) - 1

    def __iadd__(self, other: ConfusionMatrix) -> ConfusionMatrix:
        self.tp += other.tp
        self.fp += other.fp
        self.tn += other.tn
        self.fn += other.fn
        return self

    def __add__(self, other: ConfusionMatrix) -> ConfusionMatrix:
        return ConfusionMatrix(
            tp=self.tp + other.tp,
            fp=self.fp + other.fp,
            tn=self.tn + other.tn,
            fn=self.fn + other.fn,
        )


class LatencyStats(BaseModel):
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    mean_ms: float = 0.0
    max_ms: float = 0.0


class TargetConfig(BaseModel):
    base_url: str
    name: str = ""
    block_status: int = 403
    allow_status_min: int = 200
    allow_status_max: int = 299

    def is_block_status(self, status: int) -> bool:
        return status == self.block_status

    def is_allow_status(self, status: int) -> bool:
        return self.allow_status_min <= status <= self.allow_status_max


class RunConfig(BaseModel):
    target: TargetConfig
    testcase_dirs: list[str] = Field(default_factory=lambda: ["testcases"])
    tags: list[str] = Field(default_factory=list)
    exclude_tags: list[str] = Field(default_factory=list)
    encodings: list[Encoding] = Field(default_factory=lambda: [Encoding.PLAIN])
    concurrency: int = 10
    timeout: float = 10.0
    fail_under: float | None = None
    fail_fp_over: float | None = None


class TestFile(BaseModel):
    """Represents a parsed YAML test file."""

    meta: FileMeta
    tests: list[TestCase]
