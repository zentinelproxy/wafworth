<p align="center">
  <a href="https://zentinelproxy.io">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/zentinelproxy/design/main/marks/lockup/zentinel-lockup-dark.svg">
      <img alt="Zentinel" src="https://raw.githubusercontent.com/zentinelproxy/design/main/marks/lockup/zentinel-lockup-light.svg" height="52">
    </picture>
  </a>
</p>

<h3 align="center">wafworth</h3>

<p align="center">Is your WAF worth it? A WAF-agnostic test runner that sends attack and benign requests through any WAF and reports detection rate, false positives and latency.</p>

<p align="center">
  <a href="https://github.com/zentinelproxy/wafworth/actions/workflows/ci.yaml"><img alt="CI" src="https://github.com/zentinelproxy/wafworth/actions/workflows/ci.yaml/badge.svg"></a>
  <img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-9b4d8a?style=flat&labelColor=1f161e">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-f68d31?style=flat&labelColor=1f161e&logo=python&logoColor=white">
</p>

<p align="center">
  <a href="docs/getting-started.md">Getting started</a> &middot;
  <a href="https://docs.zentinelproxy.io">Docs</a> &middot;
  <a href="https://github.com/zentinelproxy">All repositories</a>
</p>

wafworth reads test cases from YAML, sends each one over HTTP to a target that
sits behind a WAF, and counts a request as blocked when the WAF answers with
the block status. Every attack can be re-sent in several encodings, and benign
requests are part of the corpus, so a WAF that blocks everything scores badly
on false positives. Results from several WAFs can be compared side by side.
It does not depend on any particular WAF; Zentinel uses it to measure its own
agents.

## Quick start

```bash
git clone https://github.com/zentinelproxy/wafworth
cd wafworth
pip install -e .

wafworth run --target http://localhost:8080 --name my-waf
```

The target must forward allowed requests to a backend that answers them; see
[Docker examples](docs/docker-examples.md).

## Install

wafworth is not on PyPI. Install from a checkout (Python 3.11 or newer):

```bash
pip install -e .            # or: pip install -e ".[dev]" for tests and ruff
```

With mise, which pins Python 3.13 and uses uv:

```bash
mise install && mise run install
```

Or build the container image (`Dockerfile`, entrypoint `wafworth`):

```bash
docker build -t wafworth .
docker run --rm --network host wafworth run -t http://localhost:8080
```

## What is in the corpus

- 598 test cases in 38 YAML files across 18 categories (`testcases/`), mapped to
  OWASP Top 10 and WSTG IDs in [OWASP_COVERAGE.md](OWASP_COVERAGE.md).
- 43 CVE-specific cases (`testcases/known-cves/`), among them Log4Shell,
  Shellshock, Spring4Shell and the 2024 Ivanti, Fortinet, PHP-CGI and xz cases.
- 120 false-positive cases: ordinary requests that must not be blocked.
- WAF bypass and evasion cases: padding, parameter pollution, HTTP/2-specific
  requests, polyglot payloads.

Counts are from `wafworth list` and `wafworth validate testcases/` on `main`.

## Usage

```bash
# Re-send every attack in several encodings, 20 requests at a time
wafworth run -t http://localhost:8080 --encodings plain,url,hex -c 20

# Only some categories
wafworth run -t http://localhost:8080 --tags sqli,xss

# Gate a pipeline: exit 1 below 95% detection or above 5% false positives
wafworth run -t http://localhost:8080 --fail-under 0.95 --fail-fp-over 0.05

# Compare saved results
wafworth compare -r results/zentinel-modsec/ -r results/zentinel-waf/

# Inspect and maintain the corpus
wafworth list --tags sqli
wafworth validate testcases/
wafworth encode "1' OR '1'='1"

# Import OWASP CRS go-ftw test files
wafworth import ftw /path/to/crs/tests/
```

`run` options:

| Option | Meaning |
|---|---|
| `-t`, `--target` | WAF URL (required) |
| `-n`, `--name` | target name used in reports |
| `--block-status` | status code that means "blocked" |
| `-d`, `--testcases` | test case directories |
| `--tags`, `--exclude-tags` | comma-separated tag filters |
| `--encodings` | `plain`, `url`, `double_url`, `hex`, `unicode_escape`, `html_entity`, `base64`, `utf7`, `overlong_utf8` |
| `-c`, `--concurrency` | maximum concurrent requests |
| `--timeout` | per-request timeout in seconds |
| `-o`, `--output` | report directory |
| `--format` | `all`, `console`, `json`, `markdown` |
| `--fail-under`, `--fail-fp-over` | CI thresholds (fractions, e.g. `0.95`) |

Requests are sent with httpx (HTTP/2 enabled, TLS verification off).

## Results in this repository

`results/` holds one run against three Zentinel setups (the WAF, ZentinelSec
and ModSecurity agents, configs in `bench/`) and their comparison. It dates
from 2026-03-04, before the zentinel-modsec CRS evaluation fixes of
August–October 2026, so it does not describe current releases. Re-run before
quoting it.

## Documentation

- [Getting started](docs/getting-started.md)
- [Writing test cases](docs/writing-test-cases.md)
- [Running tests](docs/running-tests.md)
- [Understanding results](docs/understanding-results.md)
- [Encoding and auto-generation](docs/encoding-auto-generation.md)
- [Comparing WAFs](docs/comparing-wafs.md)
- [CI integration](docs/ci-integration.md)
- [go-ftw import](docs/go-ftw-import.md)
- [Docker examples](docs/docker-examples.md)

## Development

```bash
mise run install    # venv + editable install with dev dependencies
mise run test       # pytest
mise run lint       # ruff check
mise run fmt-check  # ruff format --check
mise run validate   # validate every test case YAML file
mise run ci         # lint, format check, tests
```

CI runs lint, format check and tests on Python 3.11, 3.12 and 3.13.

## Related

- [WAF agent](https://registry.zentinelproxy.io/waf/),
  [ZentinelSec agent](https://registry.zentinelproxy.io/zentinelsec/),
  [ModSecurity agent](https://registry.zentinelproxy.io/modsec/): the WAFs measured in `results/`
- [zentinel-modsec](https://github.com/zentinelproxy/zentinel-modsec): the engine behind ZentinelSec
- [Benchmarks on zentinelproxy.io](https://zentinelproxy.io/benchmarks/)

## License

Apache-2.0, see [`LICENSE`](LICENSE).

---

<p align="center">
  <sub>Part of <a href="https://zentinelproxy.io">Zentinel</a>, the security-first reverse proxy. The shisa guards the gate.</sub>
</p>
