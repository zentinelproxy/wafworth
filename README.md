# wafworth

Is your WAF worth it? — WAF-agnostic testing framework with encoding auto-generation and multi-WAF comparison.

## Quick Start

```bash
# Install
pip install -e .

# Or with mise
mise install && mise run install

# Run against a WAF
wafworth run --target http://localhost:8080 --name my-waf
```

## Features

- **580+ test cases** across 18 attack categories, mapped to OWASP Top 10 and WSTG IDs
- **43 CVE-specific tests** — Log4Shell, Spring4Shell, PAN-OS, Ivanti, Next.js, and more (2014–2026)
- **9 encoding auto-generation** — URL, double-URL, hex, Unicode, HTML entity, base64, UTF-7, overlong UTF-8
- **WAF bypass suite** — padding evasion, parameter pollution, HTTP/2 attacks, polyglot payloads
- **Multi-WAF comparison** — side-by-side detection rate, FP rate, and latency
- **CI thresholds** — `--fail-under` and `--fail-fp-over` for pipeline gating
- **go-ftw import** — bring in OWASP CRS test files directly
- **Async executor** — httpx with HTTP/2, configurable concurrency

## Usage

```bash
# Multiple encodings
wafworth run -t http://localhost:8080 --encodings plain,url,hex -c 20

# Filter by tags
wafworth run -t http://localhost:8080 --tags sqli,xss

# Compare WAFs
wafworth compare -r results/modsec/ -r results/zentinel/

# List, validate, encode
wafworth list --tags sqli
wafworth validate testcases/
wafworth encode "1' OR '1'='1"

# Import CRS tests
wafworth import ftw /path/to/crs/tests/
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Writing Test Cases](docs/writing-test-cases.md)
- [Running Tests](docs/running-tests.md)
- [Understanding Results](docs/understanding-results.md)
- [Encoding & Auto-Generation](docs/encoding-auto-generation.md)
- [Comparing WAFs](docs/comparing-wafs.md)
- [CI Integration](docs/ci-integration.md)
- [go-ftw Import](docs/go-ftw-import.md)
- [Docker Examples](docs/docker-examples.md)

## OWASP Coverage

See [OWASP_COVERAGE.md](OWASP_COVERAGE.md) for the full coverage matrix including WSTG IDs and CVE details.

## License

Apache-2.0
