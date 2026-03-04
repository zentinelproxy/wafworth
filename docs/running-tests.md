# Running Tests

## `wafworth run`

The main command. Sends test cases to a WAF and reports results.

```bash
wafworth run --target http://localhost:8080 --name modsecurity
```

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--target` | `-t` | (required) | Target WAF URL |
| `--name` | `-n` | target URL | Name used in reports |
| `--block-status` | | `403` | HTTP status code indicating a block |
| `--testcases` | `-d` | `testcases` | Test case directories (repeatable) |
| `--tags` | | all | Comma-separated tags to include |
| `--exclude-tags` | | none | Comma-separated tags to exclude |
| `--encodings` | | `plain` | Comma-separated encodings to apply |
| `--concurrency` | `-c` | `10` | Max concurrent requests |
| `--timeout` | | `10.0` | Per-request timeout in seconds |
| `--output` | `-o` | `results` | Output directory for reports |
| `--format` | | `all` | Output format: `all`, `console`, `json`, `markdown` |
| `--fail-under` | | none | Exit 1 if detection rate below threshold |
| `--fail-fp-over` | | none | Exit 1 if false-positive rate above threshold |

### Examples

Run with multiple encodings and higher concurrency:

```bash
wafworth run -t http://localhost:8080 --encodings plain,url,hex -c 20
```

Filter to only SQL injection tests:

```bash
wafworth run -t http://localhost:8080 --tags sqli
```

Exclude high-paranoia tests:

```bash
wafworth run -t http://localhost:8080 --exclude-tags paranoia-3,paranoia-4
```

Use a custom block status code:

```bash
wafworth run -t http://localhost:8080 --block-status 406
```

## `wafworth list`

List available test cases with filtering.

```bash
wafworth list
wafworth list --tags sqli
wafworth list --severity critical
wafworth list --categories "SQL Injection,XSS"
```

Shows a summary table by category and top tags.

## `wafworth validate`

Validate YAML test case files for correct structure.

```bash
wafworth validate testcases/
```

Exits with code 1 if any files have errors.

## `wafworth encode`

Show how a payload looks under every supported encoding:

```bash
wafworth encode "1' OR '1'='1"
```

Prints a table with all 9 encoding variants. Useful for understanding what the encoding expansion does before running tests.
