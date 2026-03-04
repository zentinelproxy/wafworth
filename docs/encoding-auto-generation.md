# Encoding & Auto-Generation

wafworth can automatically expand each test case across multiple payload encodings, simulating common WAF bypass techniques per [OWASP WSTG-INPV-01](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/01-Testing_for_Reflected_Cross_Site_Scripting).

## Supported Encodings

| Encoding | Description | Example: `<script>` |
|----------|-------------|----------------------|
| `plain` | No encoding (original payload) | `<script>` |
| `url` | Standard URL/percent encoding | `%3Cscript%3E` |
| `double_url` | Double URL encoding | `%253Cscript%253E` |
| `hex` | Hex encoding of all bytes | `%3c%73%63%72%69%70%74%3e` |
| `unicode_escape` | Unicode escape sequences | `\u003cscript\u003e` |
| `html_entity` | HTML entity encoding | `&lt;script&gt;` |
| `base64` | Base64 encoding | `PHNjcmlwdD4=` |
| `utf7` | UTF-7-style encoding | `+ADw-script+AD4-` |
| `overlong_utf8` | Overlong UTF-8 sequences | `%c0%bc script%c0%be` |

## How Expansion Works

When you specify `--encodings plain,url,hex`:

1. Each attack test case is duplicated for each encoding
2. Query string values and request bodies are encoded (keys are preserved)
3. Test IDs are suffixed: `sqli-001` becomes `sqli-001:url`, `sqli-001:hex`
4. False-positive tests are **only** run with `plain` — encoding legitimate traffic is meaningless for FP measurement

With 580 base tests and 3 encodings, you get ~1,740 test executions (minus FP tests not expanded).

## Encoding-to-Bypass Table

| Encoding | Bypasses |
|----------|----------|
| `url` | Basic WAF rules that don't URL-decode before matching |
| `double_url` | WAFs that decode once but not twice |
| `hex` | Rules that only match ASCII characters |
| `unicode_escape` | WAFs without Unicode normalization |
| `html_entity` | Rules matching raw characters in HTML context |
| `base64` | WAFs that don't decode base64 parameters |
| `utf7` | Legacy UTF-7 auto-detection in older browsers/parsers |
| `overlong_utf8` | WAFs with strict UTF-8 validation that don't reject overlong sequences |

## The `encode` Command

Preview all encodings for a payload without running tests:

```bash
wafworth encode "<script>alert(1)</script>"
```

This prints a table showing each encoding applied to the given payload.

## Choosing Encodings

- **Quick scan**: `--encodings plain` (default) — fastest, baseline detection
- **Standard**: `--encodings plain,url,double_url` — catches the most common bypass gaps
- **Thorough**: `--encodings plain,url,double_url,hex,unicode_escape,html_entity,base64,utf7,overlong_utf8` — full coverage
