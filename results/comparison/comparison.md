# WAF Comparison

## Overall Metrics

| Metric | zentinel-waf | zentinel-zentinelsec | zentinel-modsec |
|--------| ---: | ---: | ---: |
| Detection Rate | 43.1% | 38.7% | 32.1% |
| FP Rate | 9.0% | 2.5% | 2.5% |
| Precision | 94.9% | 98.4% | 98.1% |
| F1 Score | 59.2% | 55.5% | 48.4% |
| Balanced Accuracy | 67.0% | 68.1% | 64.8% |

## Detection Rate by Category

| Category | zentinel-waf | zentinel-zentinelsec | zentinel-modsec |
|----------| ---: | ---: | ---: |
| API Security | 0.0% | 0.0% | 0.0% |
| Authentication Attacks | 20.0% | 20.0% | 20.0% |
| Command Injection | 3.3% | 3.3% | 3.3% |
| Cross-Site Scripting | 73.3% | 70.0% | 70.0% |
| Deserialization | 8.3% | 0.0% | 0.0% |
| Evasion Techniques | 24.0% | 52.0% | 48.0% |
| False Positives | 0.0% | 0.0% | 0.0% |
| File Upload | 0.0% | 0.0% | 0.0% |
| Known CVEs | 54.1% | 18.9% | 16.2% |
| Path Traversal | 80.0% | 50.0% | 53.3% |
| Protocol Attacks | 31.6% | 10.5% | 5.3% |
| ReDoS | 20.0% | 0.0% | 0.0% |
| SQL Injection | 37.5% | 66.7% | 25.0% |
| Scanner Detection | 80.0% | 6.7% | 33.3% |
| Server-Side Request Forgery | 80.0% | 60.0% | 60.0% |
| Server-Side Template Injection | 60.0% | 53.3% | 46.7% |
| WAF Bypass | 56.1% | 51.5% | 48.5% |
| XML External Entities | 0.0% | 0.0% | 0.0% |
