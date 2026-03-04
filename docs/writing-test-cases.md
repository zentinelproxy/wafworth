# Writing Test Cases

Test cases are YAML files in the `testcases/` directory, organized by category.

## File Structure

Each YAML file contains a `meta` block and a `tests` list:

```yaml
meta:
  category: "SQL Injection"
  subcategory: "Advanced"
  owasp: "A03:2021, WSTG-INPV-05"
  severity: "critical"

tests:
  - id: "sqli-adv-001"
    title: "Error-based extraction via EXTRACTVALUE"
    tags: ["sqli", "advanced", "error-based", "paranoia-1"]
    request:
      method: "GET"
      path: "/api/products"
      query_string: "id=1 AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version()),0x7e))--"
    expected:
      status: 403
      action: "block"
```

## Meta Fields

| Field | Required | Description |
|-------|----------|-------------|
| `category` | Yes | Attack category (e.g. "SQL Injection", "XSS") |
| `subcategory` | No | Sub-grouping within the category |
| `owasp` | No | OWASP Top 10 ID (e.g. "A03:2021") and/or WSTG ID (e.g. "WSTG-INPV-05") |
| `severity` | No | One of: `critical`, `high`, `medium`, `low`, `info` (default: `medium`) |

## Test Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique test identifier |
| `title` | Yes | Human-readable description |
| `tags` | No | List of tags for filtering |
| `request.method` | No | HTTP method (default: `GET`) |
| `request.path` | No | Request path (default: `/`) |
| `request.query_string` | No | Query string (without leading `?`) |
| `request.headers` | No | Dictionary of HTTP headers |
| `request.body` | No | Request body string |
| `request.content_type` | No | Content-Type header shortcut |
| `expected.action` | No | `block` or `allow` (default: `block`) |
| `expected.status` | No | Expected HTTP status code (default: `403` for block, `200` for allow) |

## Tagging Conventions

Tags are used for filtering with `--tags` and `--exclude-tags`. Common conventions:

- **Category**: `sqli`, `xss`, `cmdi`, `ssti`, `ssrf`, etc.
- **Technique**: `error-based`, `blind`, `union`, `polyglot`
- **Paranoia level**: `paranoia-1` through `paranoia-4` (CRS-aligned)
- **Protocol**: `http2`, `header`, `body`, `query`

## False-Positive Tests

Tests with `action: "allow"` represent legitimate traffic that the WAF should **not** block. These measure false-positive rates:

```yaml
  - id: "fp-api-001"
    title: "Legitimate API pagination request"
    tags: ["false-positive", "api"]
    request:
      method: "GET"
      path: "/api/users"
      query_string: "page=1&limit=50&sort=name"
    expected:
      action: "allow"
      status: 200
```

False-positive tests are only run with `plain` encoding — encoding legitimate traffic for bypass testing doesn't make sense.

## Validating Test Files

Check that all YAML files parse correctly:

```bash
wafworth validate testcases/
```

This verifies structure, required fields, and unique IDs.
