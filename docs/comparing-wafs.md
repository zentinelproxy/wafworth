# Comparing WAFs

wafworth can compare results from multiple WAF targets side by side.

## Workflow

### 1. Run tests against each WAF

```bash
wafworth run -t http://localhost:8080 -n modsecurity -o results/modsec/
wafworth run -t http://localhost:8081 -n coraza -o results/coraza/
wafworth run -t http://localhost:8082 -n zentinel -o results/zentinel/
```

### 2. Compare results

```bash
wafworth compare --results results/modsec/ results/coraza/ results/zentinel/
```

You can also point to individual JSON files:

```bash
wafworth compare -r results/modsec/results.json -r results/coraza/results.json
```

## Compare Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--results` | `-r` | (required) | Result JSON files or directories (repeatable, min 2) |
| `--output` | `-o` | `results/comparison` | Output directory |
| `--format` | | `all` | Output format: `all`, `console`, `json`, `markdown` |

## Output

The comparison shows:

- **Overall metrics** for each target: detection rate, FP rate, precision, F1
- **Per-category differences**: which WAF catches more attacks in each category
- **Per-encoding differences**: how each WAF handles encoded payloads
- **Latency comparison**: response time percentiles for each target

### Console Output

A side-by-side table in the terminal with color-coded differences.

### JSON Output

A structured JSON file with all comparison data, suitable for dashboards or further analysis.

### Markdown Output

A Markdown table ready for PR descriptions, wiki pages, or issue trackers.
