"""Payload encoding engine with auto-expansion of test cases."""

from __future__ import annotations

import base64
import html
from urllib.parse import quote

from .models import Encoding, ExpandedTestCase, TestCase, TestRequest


def encode_url(payload: str) -> str:
    return quote(payload, safe="")


def encode_double_url(payload: str) -> str:
    return quote(quote(payload, safe=""), safe="")


def encode_hex(payload: str) -> str:
    return "".join(f"%{b:02x}" for b in payload.encode())


def encode_unicode_escape(payload: str) -> str:
    return "".join(f"\\u{ord(c):04x}" if not c.isascii() or not c.isalnum() else c for c in payload)


def encode_html_entity(payload: str) -> str:
    return html.escape(payload, quote=True)


def encode_base64(payload: str) -> str:
    return base64.b64encode(payload.encode()).decode()


def encode_utf7(payload: str) -> str:
    """Encode using a UTF-7-like +ADw- style for angle brackets and special chars."""
    result = []
    for c in payload:
        if c == "<":
            result.append("+ADw-")
        elif c == ">":
            result.append("+AD4-")
        elif c == '"':
            result.append("+ACE-")
        elif c == "'":
            result.append("+ACc-")
        else:
            result.append(c)
    return "".join(result)


def encode_overlong_utf8(payload: str) -> str:
    """Encode ASCII chars using overlong UTF-8 sequences (percent-encoded)."""
    result = []
    for c in payload:
        b = ord(c)
        if 0x20 <= b <= 0x7E and not c.isalnum():
            # 2-byte overlong encoding for ASCII
            b1 = 0xC0 | (b >> 6)
            b2 = 0x80 | (b & 0x3F)
            result.append(f"%{b1:02x}%{b2:02x}")
        else:
            result.append(c)
    return "".join(result)


ENCODERS: dict[Encoding, callable] = {
    Encoding.URL: encode_url,
    Encoding.DOUBLE_URL: encode_double_url,
    Encoding.HEX: encode_hex,
    Encoding.UNICODE_ESCAPE: encode_unicode_escape,
    Encoding.HTML_ENTITY: encode_html_entity,
    Encoding.BASE64: encode_base64,
    Encoding.UTF7: encode_utf7,
    Encoding.OVERLONG_UTF8: encode_overlong_utf8,
}


def encode_payload(payload: str, encoding: Encoding) -> str:
    """Encode a payload string with the given encoding."""
    if encoding == Encoding.PLAIN:
        return payload
    encoder = ENCODERS.get(encoding)
    if encoder is None:
        raise ValueError(f"Unknown encoding: {encoding}")
    return encoder(payload)


def _encode_query_string(qs: str, encoding: Encoding) -> str:
    """Encode query string values (not keys) with the given encoding."""
    if not qs:
        return qs
    parts = []
    for param in qs.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            parts.append(f"{key}={encode_payload(value, encoding)}")
        else:
            parts.append(param)
    return "&".join(parts)


def _encode_request(request: TestRequest, encoding: Encoding) -> TestRequest:
    """Create a new TestRequest with encoded payloads."""
    new_qs = _encode_query_string(request.query_string, encoding)
    new_body = encode_payload(request.body, encoding) if request.body else request.body
    return TestRequest(
        method=request.method,
        path=request.path,
        query_string=new_qs,
        headers=dict(request.headers),
        body=new_body,
        content_type=request.content_type,
    )


def expand_test_case(tc: TestCase, encodings: list[Encoding]) -> list[ExpandedTestCase]:
    """Expand a test case into multiple encoded variants.

    False-positive tests are only run with plain encoding since encoding
    legitimate traffic doesn't make sense for FP measurement.
    """
    results: list[ExpandedTestCase] = []

    for enc in encodings:
        if tc.is_false_positive and enc != Encoding.PLAIN:
            continue

        if enc == Encoding.PLAIN:
            results.append(
                ExpandedTestCase(
                    test_case=tc,
                    encoding=Encoding.PLAIN,
                    original_id=tc.id,
                )
            )
        else:
            encoded_req = _encode_request(tc.request, enc)
            results.append(
                ExpandedTestCase(
                    test_case=tc,
                    encoding=enc,
                    original_id=tc.id,
                    encoded_request=encoded_req,
                )
            )

    return results


def expand_all(test_cases: list[TestCase], encodings: list[Encoding]) -> list[ExpandedTestCase]:
    """Expand all test cases with the given encodings."""
    results: list[ExpandedTestCase] = []
    for tc in test_cases:
        results.extend(expand_test_case(tc, encodings))
    return results
