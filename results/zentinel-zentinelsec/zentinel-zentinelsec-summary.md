# WAF Test Results — zentinel-zentinelsec

**Total**: 598 | **Passed**: 303 | **Failed**: 295

## Overall Metrics

| Metric | Value |
|--------|-------|
| Detection Rate | 38.7% |
| False Positive Rate | 2.5% |
| Precision | 98.4% |
| F1 Score | 55.5% |
| Balanced Accuracy | 68.1% |
| Youden's J | 0.362 |

## Latency

p50=2.6ms | p95=3.1ms | p99=3.6ms | mean=2.6ms

## Per-Category Breakdown

| Category | TP | FP | TN | FN | Detection | FP Rate |
|----------|---:|---:|---:|---:|----------:|--------:|
| API Security | 0 | 0 | 8 | 20 | 0.0% | 0.0% |
| Authentication Attacks | 4 | 0 | 0 | 16 | 20.0% | 0.0% |
| Command Injection | 1 | 0 | 8 | 29 | 3.3% | 0.0% |
| Cross-Site Scripting | 42 | 0 | 2 | 18 | 70.0% | 0.0% |
| Deserialization | 0 | 0 | 3 | 12 | 0.0% | 0.0% |
| Evasion Techniques | 13 | 0 | 5 | 12 | 52.0% | 0.0% |
| False Positives | 0 | 1 | 49 | 0 | 0.0% | 2.0% |
| File Upload | 0 | 0 | 0 | 15 | 0.0% | 0.0% |
| Known CVEs | 7 | 0 | 6 | 30 | 18.9% | 0.0% |
| Path Traversal | 15 | 0 | 8 | 15 | 50.0% | 0.0% |
| Protocol Attacks | 2 | 1 | 6 | 17 | 10.5% | 14.3% |
| ReDoS | 0 | 0 | 0 | 10 | 0.0% | 0.0% |
| SQL Injection | 48 | 0 | 3 | 24 | 66.7% | 0.0% |
| Scanner Detection | 1 | 0 | 10 | 14 | 6.7% | 0.0% |
| Server-Side Request Forgery | 9 | 0 | 5 | 6 | 60.0% | 0.0% |
| Server-Side Template Injection | 8 | 1 | 2 | 7 | 53.3% | 33.3% |
| WAF Bypass | 34 | 0 | 0 | 32 | 51.5% | 0.0% |
| XML External Entities | 0 | 0 | 4 | 15 | 0.0% | 0.0% |

## Failures (295)

- **api-001**: expected block (status 403), got 200 — GraphQL introspection query
- **api-002**: expected block (status 403), got 200 — GraphQL deeply nested query (DoS)
- **api-003**: expected block (status 403), got 200 — GraphQL batch query (DoS)
- **api-004**: expected block (status 403), got 200 — GraphQL alias-based DoS
- **api-005**: expected block (status 403), got 200 — GraphQL SQLi in variable
- **api-006**: expected block (status 403), got 200 — JWT none algorithm
- **api-007**: expected block (status 403), got 200 — JWT algorithm confusion (RS256 to HS256)
- **api-008**: expected block (status 403), got 200 — JWT with jwk header injection
- **api-009**: expected block (status 403), got 200 — JSON depth bomb
- **api-010**: expected block (status 403), got 200 — JSON key bomb
- **api-011**: expected block (status 403), got 200 — Mass assignment via JSON
- **api-012**: expected block (status 403), got 200 — BOLA - accessing other user resources
- **api-013**: expected block (status 403), got 200 — API version bypass
- **api-014**: expected block (status 403), got 200 — Content-Type mismatch attack
- **api-015**: expected block (status 403), got 200 — Prototype pollution via JSON
- **api-016**: expected block (status 403), got 200 — Prototype pollution via constructor
- **api-017**: expected block (status 403), got 200 — REST API enumeration via sequential IDs
- **api-018**: expected block (status 403), got 200 — GraphQL mutation with XSS
- **api-019**: expected block (status 403), got 200 — OpenAPI/Swagger endpoint probe
- **api-020**: expected block (status 403), got 200 — GraphQL field suggestion abuse
- **auth-brute-001**: expected block (status 403), got 200 — Common credential pair admin:admin
- **auth-brute-002**: expected block (status 403), got 200 — Common credential pair admin:password
- **auth-brute-003**: expected block (status 403), got 200 — Common credential pair root:toor
- **auth-brute-004**: expected block (status 403), got 200 — Common credential pair admin:123456
- **auth-jwt-001**: expected block (status 403), got 200 — JWT with alg:none bypass
- **auth-jwt-002**: expected block (status 403), got 200 — JWT with alg:None (capitalized) bypass
- **auth-jwt-003**: expected block (status 403), got 200 — JWT algorithm confusion RS256 to HS256
- **auth-jwt-004**: expected block (status 403), got 200 — JWT with JWK header injection
- **auth-session-001**: expected block (status 403), got 200 — Session ID in URL parameter
- **auth-session-002**: expected block (status 403), got 200 — Session token in URL (PHPSESSID)
- **auth-admin-002**: expected block (status 403), got 200 — phpMyAdmin default access
- **auth-admin-004**: expected block (status 403), got 200 — Kubernetes dashboard access
- **auth-admin-005**: expected block (status 403), got 501 — Debug/trace endpoint access
- **auth-admin-008**: expected block (status 403), got 200 — AWS credentials file
- **auth-admin-009**: expected block (status 403), got 200 — Docker socket exposure
- **auth-admin-010**: expected block (status 403), got 200 — Backup file exposure (.bak)
- **cmdi-adv-001**: expected block (status 403), got 200 — Perl reverse shell
- **cmdi-adv-002**: expected block (status 403), got 200 — Ruby command execution via system()
- **cmdi-adv-003**: expected block (status 403), got 200 — Netcat reverse shell with -e flag
- **cmdi-adv-004**: expected block (status 403), got 200 — Mkfifo-based reverse shell
- **cmdi-adv-005**: expected block (status 403), got 200 — Crontab injection for persistence
- **cmdi-adv-007**: expected block (status 403), got 200 — Command injection via IFS variable substitution
- **cmdi-adv-008**: expected block (status 403), got 200 — Windows net user account creation
- **cmdi-adv-009**: expected block (status 403), got 200 — Data exfiltration via DNS
- **cmdi-adv-010**: expected block (status 403), got 200 — Command injection via ANSI-C quoting
- **cmdi-001**: expected block (status 403), got 200 — Semicolon command injection
- **cmdi-002**: expected block (status 403), got 200 — Pipe command injection
- **cmdi-003**: expected block (status 403), got 200 — Command substitution $()
- **cmdi-004**: expected block (status 403), got 200 — Backtick injection
- **cmdi-005**: expected block (status 403), got 200 — AND operator injection
- ... and 245 more
