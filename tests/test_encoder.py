"""Tests for payload encoder."""

from wafworth.encoder import (
    encode_base64,
    encode_double_url,
    encode_hex,
    encode_html_entity,
    encode_overlong_utf8,
    encode_payload,
    encode_url,
    encode_utf7,
    expand_test_case,
)
from wafworth.models import (
    Encoding,
    TestCase,
    TestExpected,
    TestRequest,
)


def test_encode_url():
    assert encode_url("1' OR '1'='1") == "1%27%20OR%20%271%27%3D%271"


def test_encode_double_url():
    result = encode_double_url("' OR 1=1--")
    assert "%25" in result  # double-encoded %


def test_encode_hex():
    result = encode_hex("abc")
    assert result == "%61%62%63"


def test_encode_html_entity():
    result = encode_html_entity("<script>alert(1)</script>")
    assert "&lt;" in result
    assert "&gt;" in result


def test_encode_base64():
    result = encode_base64("test payload")
    assert result == "dGVzdCBwYXlsb2Fk"


def test_encode_utf7():
    result = encode_utf7("<script>")
    assert "+ADw-" in result
    assert "+AD4-" in result


def test_encode_overlong_utf8():
    result = encode_overlong_utf8("a<b")
    # < should be overlong encoded, a and b should remain
    assert result.startswith("a")
    assert "b" in result
    assert "%" in result


def test_encode_payload_plain():
    assert encode_payload("test", Encoding.PLAIN) == "test"


def test_expand_test_case_attack():
    tc = TestCase(
        id="sqli-001",
        title="Test",
        tags=["sqli"],
        request=TestRequest(method="GET", path="/", query_string="id=1' OR 1=1"),
        expected=TestExpected(action="block", status=403),
    )

    expanded = expand_test_case(tc, [Encoding.PLAIN, Encoding.URL, Encoding.HEX])
    assert len(expanded) == 3
    assert expanded[0].encoding == Encoding.PLAIN
    assert expanded[1].encoding == Encoding.URL
    assert expanded[2].encoding == Encoding.HEX

    # URL-encoded version should have encoded query values
    url_req = expanded[1].effective_request
    assert "%27" in url_req.query_string or "%20" in url_req.query_string


def test_expand_test_case_fp_skips_encodings():
    tc = TestCase(
        id="fp-001",
        title="Legitimate",
        tags=["false-positive"],
        request=TestRequest(method="GET", path="/"),
        expected=TestExpected(action="allow", status=200),
    )

    expanded = expand_test_case(tc, [Encoding.PLAIN, Encoding.URL, Encoding.HEX])
    assert len(expanded) == 1  # Only plain
    assert expanded[0].encoding == Encoding.PLAIN


def test_expanded_effective_id():
    tc = TestCase(
        id="xss-001",
        title="Test",
        request=TestRequest(),
        expected=TestExpected(action="block", status=403),
    )

    expanded = expand_test_case(tc, [Encoding.PLAIN, Encoding.URL])
    assert expanded[0].effective_id == "xss-001"
    assert expanded[1].effective_id == "xss-001:url"
