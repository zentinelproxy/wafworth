# CI Integration

wafworth provides two threshold flags for CI pipelines that control the exit code.

## Threshold Flags

| Flag | Description |
|------|-------------|
| `--fail-under <float>` | Exit 1 if detection rate is below this value (e.g. `0.95` for 95%) |
| `--fail-fp-over <float>` | Exit 1 if false-positive rate is above this value (e.g. `0.05` for 5%) |

Both can be used together:

```bash
wafworth run -t http://waf:8080 --fail-under 0.95 --fail-fp-over 0.05
```

## GitHub Actions Example

```yaml
name: WAF Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  waf-test:
    runs-on: ubuntu-latest

    services:
      waf:
        image: owasp/modsecurity-crs:nginx-alpine
        ports:
          - 8080:8080
        env:
          PARANOIA: 1
          ANOMALY_INBOUND: 5
          BACKEND: http://localhost:80

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install wafworth
        run: pip install -e .

      - name: Wait for WAF
        run: |
          for i in $(seq 1 30); do
            curl -s -o /dev/null http://localhost:8080/ && break
            sleep 1
          done

      - name: Run WAF tests
        run: |
          wafworth run \
            --target http://localhost:8080 \
            --name modsecurity \
            --fail-under 0.90 \
            --fail-fp-over 0.10 \
            --output results/

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: waf-results
          path: results/
```

## Tips

- Start with lenient thresholds (`--fail-under 0.80`) and tighten as you tune your WAF
- Use `--format json` to produce machine-readable output for custom dashboards
- The `--tags` flag lets you run only critical tests in CI for speed, and the full suite on a schedule
