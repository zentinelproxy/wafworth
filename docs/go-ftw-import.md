# go-ftw Import

wafworth can import test cases from [go-ftw](https://github.com/coreruleset/go-ftw) format, used by the OWASP Core Rule Set (CRS).

## Usage

Import a single file:

```bash
wafworth import ftw /path/to/crs-test.yaml --output testcases/
```

Import a directory:

```bash
wafworth import ftw /path/to/crs/tests/ --output testcases/
```

Imported tests are organized into subdirectories by category and written as wafworth YAML files.

## CRS Rule ID Category Mapping

go-ftw tests are identified by CRS rule IDs. wafworth maps these to categories:

| Rule ID Prefix | Category |
|---------------|----------|
| 910 | Scanner Detection |
| 911, 912 | Protocol Enforcement |
| 913 | Scanner Detection |
| 920, 921 | Protocol |
| 930, 931 | Path Traversal |
| 932 | Command Injection |
| 933, 934 | SSTI |
| 941 | XSS |
| 942 | SQL Injection |
| 943 | Session Fixation |
| 944 | Deserialization |
| 949, 959 | Blocking |
| 950, 951, 953, 954 | Data Leakage |
| 980 | Correlation |

Unmapped rule IDs are categorized as "Other".

## Test ID Format

Imported tests get IDs in the format `crs-{rule_id}-{index}`, e.g. `crs-942-001`.

Tags include the category, `crs`, and the specific rule reference (`crs-942`).

## Limitations

- **`encoded_request`**: go-ftw tests that use raw `encoded_request` fields are skipped (wafworth handles encoding separately)
- **`dest_addr` / custom ports**: Tests targeting specific hosts or ports beyond the WAF endpoint are skipped
- **`no_log_contains`**: go-ftw log-based assertions are converted to `action: allow` since wafworth tests via HTTP responses, not WAF logs
- **Status arrays**: go-ftw allows multiple expected statuses (`[403, 406]`); wafworth uses the first value
