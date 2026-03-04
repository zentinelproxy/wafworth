# wafworth

OWASP-aligned, WAF-agnostic testing framework with encoding auto-generation and multi-WAF comparison.

Test cases are systematically mapped to the [OWASP Top 10 (2021)](https://owasp.org/Top10/) and the [OWASP Web Security Testing Guide (WSTG) v4.2](https://owasp.org/www-project-web-security-testing-guide/). See [OWASP_COVERAGE.md](OWASP_COVERAGE.md) for the full coverage matrix.

## Features

- **580+ test cases** across 18 attack categories, mapped to OWASP Top 10 and WSTG IDs
- **Full OWASP Top 10 2021 coverage**: A01 (Access Control), A03 (Injection), A05 (Misconfiguration), A06 (Vulnerable Components), A07 (Auth Failures), A08 (Data Integrity), A10 (SSRF), and more
- **43 CVE-specific tests**: Log4Shell, Spring4Shell, React2Shell, PAN-OS, Ivanti, Next.js, Tomcat, Jenkins (2014-2026)
- **WAF bypass suite**: padding evasion, parameter pollution, HTTP/2 attacks, polyglot payloads, vendor-specific bypasses (Cloudflare/AWS/Akamai patterns)
- **Encoding auto-generation**: multiply base tests by 9 encodings (URL, double-URL, hex, Unicode, HTML entity, base64, UTF-7, overlong UTF-8) per WSTG-INPV-01
- **WAF-agnostic**: configurable block status codes per target (403, 406, 418, etc.)
- **Async executor**: httpx with HTTP/2, semaphore-based concurrency
- **Rich metrics**: balanced accuracy, Youden's index, per-encoding breakdown, per-category confusion matrices
- **go-ftw compatibility**: import OWASP CRS test files directly
- **Multi-WAF comparison**: side-by-side detection rate, FP rate, and latency
- **CI integration**: `--fail-under` and `--fail-fp-over` flags for exit code control

## OWASP Test Coverage

| OWASP Top 10 | Category | Tests |
|-------------|----------|-------|
| A01:2021 | Broken Access Control | path-traversal, api-security, authentication |
| A03:2021 | Injection | sqli (75), xss (62), cmdi (38), ssti (18) |
| A05:2021 | Security Misconfiguration | protocol, xxe, evasion |
| A06:2021 | Vulnerable Components | known-cves (43 CVEs, 2014-2026) |
| A07:2021 | Auth Failures | scanner-detection, authentication |
| A08:2021 | Data Integrity | deserialization (Java/PHP/Python/.NET/Ruby) |
| A10:2021 | SSRF | ssrf (cloud metadata, localhost, protocols) |

Additional: WAF bypass (padding, HPP, HTTP/2, polyglots), file upload attacks, ReDoS, false positives.

See [OWASP_COVERAGE.md](OWASP_COVERAGE.md) for WSTG ID mapping and CVE details.

## Install

```bash
pip install -e .
```

## Usage

### Run tests against a WAF

```bash
wafworth run --target http://localhost:8080 --name modsecurity
```

### Run with multiple encodings

```bash
wafworth run --target http://localhost:8080 --encodings plain,url,hex --concurrency 20
```

### Filter by tags

```bash
wafworth run --target http://localhost:8080 --tags sqli,xss --exclude-tags paranoia-4
```

### CI mode with thresholds

```bash
wafworth run --target http://localhost:8080 --fail-under 0.95 --fail-fp-over 0.05
```

### Compare multiple WAFs

```bash
wafworth compare --results results/modsec/ results/zentinel/ --output comparison/
```

### List test cases

```bash
wafworth list --tags sqli
```

### Validate test files

```bash
wafworth validate testcases/
```

### Encode a payload

```bash
wafworth encode "1' OR '1'='1"
```

### Import go-ftw CRS tests

```bash
wafworth import ftw /path/to/crs/tests/ --output testcases/
```

## Docker examples

See `examples/` for Docker Compose setups for ModSecurity+Nginx, Coraza+Caddy, and Zentinel.

```bash
cd examples/modsecurity-nginx
docker compose up -d
wafworth run --target http://localhost:8080 --name modsecurity --output results/modsec/
```

## Development

```bash
pip install -e ".[dev]"
pytest -v
ruff check src/ tests/
```

## References

- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [OWASP Web Security Testing Guide v4.2](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP ModSecurity Core Rule Set](https://coreruleset.org/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)

## License

Apache-2.0
