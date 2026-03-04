# Getting Started

## Prerequisites

- Python 3.11+ (3.13 recommended)
- A running WAF target to test against (see [Docker Examples](docker-examples.md) for quick setups)

## Installation

### With pip

```bash
pip install -e .
```

### With uv

```bash
uv venv && uv pip install -e ".[dev]"
```

### With mise (recommended)

[mise](https://mise.jdx.dev/) manages Python, uv, and task shortcuts:

```bash
mise install
mise run install
```

## First Run

Start a WAF target. For example, using the included ModSecurity compose file:

```bash
cd examples/modsecurity-nginx
docker compose up -d
```

Run the full test suite against it:

```bash
wafworth run --target http://localhost:8080 --name modsecurity
```

This loads all test cases from `testcases/`, sends each request to the target, and produces a console summary plus JSON and Markdown reports in `results/`.

## Next Steps

- [Writing Test Cases](writing-test-cases.md) to add your own tests
- [Running Tests](running-tests.md) for filtering, concurrency, and output options
- [Encoding & Auto-Generation](encoding-auto-generation.md) to multiply tests across bypass encodings
