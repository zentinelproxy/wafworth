# OWASP Coverage Matrix

waf-playbook test cases are systematically mapped to the **OWASP Top 10 (2021)** and the **OWASP Web Security Testing Guide (WSTG) v4.2**. Each test case file includes OWASP references in its `meta.owasp` field.

## OWASP Top 10 (2021) Coverage

| # | Category | Coverage | Test Files | Tests |
|---|----------|----------|------------|-------|
| A01 | Broken Access Control | Full | `path-traversal/`, `api-security/`, `authentication/` | ~86 |
| A02 | Cryptographic Failures | Partial | `authentication/auth.yaml` (JWT attacks) | ~4 |
| A03 | Injection | Full | `sqli/`, `xss/`, `command-injection/`, `ssti/` | ~213 |
| A04 | Insecure Design | Partial | `api-security/api.yaml` (BOLA, mass assignment) | ~10 |
| A05 | Security Misconfiguration | Full | `protocol/`, `xxe/`, `evasion/` | ~75 |
| A06 | Vulnerable Components | Full | `known-cves/` (2014-2026) | ~43 |
| A07 | Auth Failures | Full | `scanner-detection/`, `authentication/` | ~45 |
| A08 | Data Integrity Failures | Full | `deserialization/` | ~15 |
| A09 | Logging & Monitoring | Indirect | Covered via scanner detection | ~25 |
| A10 | SSRF | Full | `ssrf/` | ~20 |

## OWASP WSTG (Web Security Testing Guide) Coverage

| WSTG ID | Test Area | waf-playbook Category |
|---------|-----------|----------------------|
| WSTG-INFO-02 | Fingerprint Web Server | `scanner-detection/` |
| WSTG-CONF-04 | Backup/Unreferenced Files | `authentication/auth.yaml` (admin paths) |
| WSTG-CONF-10 | HTTP Methods | `protocol/` |
| WSTG-ATHN-03 | Weak Authentication | `authentication/auth.yaml` |
| WSTG-ATHZ-01 | Directory Traversal | `path-traversal/` |
| WSTG-SESS-03 | Session Fixation | `authentication/auth.yaml` |
| WSTG-INPV-04 | HTTP Parameter Pollution | `waf-bypass/parameter-pollution.yaml` |
| WSTG-INPV-05 | SQL Injection | `sqli/` |
| WSTG-INPV-07 | XML Injection / XXE | `xxe/` |
| WSTG-INPV-12 | Command Injection | `command-injection/` |
| WSTG-INPV-15 | HTTP Incoming Requests | `redos/` |
| WSTG-INPV-18 | Server-Side Template Injection | `ssti/` |
| WSTG-INPV-19 | SSRF | `ssrf/` |
| WSTG-CLNT-01 | DOM-Based XSS | `xss/` |
| WSTG-BUSL-08 | Upload of Unexpected Files | `file-upload/` |
| WSTG-APIT-01 | API Testing | `api-security/` |

## Additional Coverage (Beyond OWASP)

| Category | Source | waf-playbook Directory |
|----------|--------|----------------------|
| WAF Padding Evasion | 2026 WAF Comparison Project | `waf-bypass/padding.yaml` |
| Parameter Pollution | Community research 2025 | `waf-bypass/parameter-pollution.yaml` |
| HTTP/2 Attacks | HTTP/2 security research | `waf-bypass/http2.yaml` |
| Polyglot Payloads | Portswigger, HackerOne | `waf-bypass/polyglot.yaml` |
| Vendor WAF Bypasses | waf-bypass.com, community | `waf-bypass/vendor-specific.yaml` |
| ReDoS Patterns | OWASP ReDoS | `redos/redos.yaml` |
| Recent CVEs (2024-2026) | NVD, vendor advisories | `known-cves/cves-2024-2026.yaml` |
| False Positives | Operational baseline | `false-positives/` |

## CVE Coverage

### Pre-2024
- CVE-2014-6271 (Shellshock)
- CVE-2017-5638 (Apache Struts)
- CVE-2017-9841 (PHPUnit RCE)
- CVE-2019-2725 (WebLogic)
- CVE-2021-22214 (GitLab SSRF)
- CVE-2021-41773 / CVE-2021-42013 (Apache path traversal)
- CVE-2021-44228 (Log4Shell)
- CVE-2022-1388 (F5 BIG-IP)
- CVE-2022-22963 (Spring Cloud Function)
- CVE-2022-22965 (Spring4Shell)
- CVE-2022-26134 (Confluence OGNL)
- CVE-2022-42889 (Text4Shell)
- CVE-2023-34362 (MOVEit Transfer)

### 2024
- CVE-2024-0012 (PAN-OS auth bypass)
- CVE-2024-1709 (ConnectWise ScreenConnect)
- CVE-2024-3094 (XZ Utils)
- CVE-2024-3400 (PAN-OS command injection)
- CVE-2024-4577 (PHP CGI argument injection)
- CVE-2024-6387 (regreSSHion)
- CVE-2024-21762 (FortiOS)
- CVE-2024-21887 (Ivanti Connect Secure)
- CVE-2024-23897 (Jenkins CLI)
- CVE-2024-27198 (JetBrains TeamCity)

### 2025-2026
- CVE-2025-0282 (Ivanti Connect Secure)
- CVE-2025-1097 (Kubernetes Ingress-Nginx)
- CVE-2025-24813 (Apache Tomcat partial PUT)
- CVE-2025-29927 (Next.js middleware bypass)
- CVE-2025-30208 (Vite dev server)
- React2Shell pattern (padded RCE)

## Encoding Evasion Matrix

All attack test cases can be automatically expanded with these encodings:

| Encoding | OWASP Ref | Bypass Target |
|----------|-----------|---------------|
| `plain` | Baseline | Direct signature match |
| `url` | WSTG-INPV-01 | URL-decoding normalization |
| `double_url` | WSTG-INPV-01 | Double-decode vulnerabilities |
| `hex` | WSTG-INPV-01 | Hex representation bypass |
| `unicode_escape` | WSTG-INPV-01 | Unicode normalization |
| `html_entity` | WSTG-INPV-01 | HTML entity decoding |
| `base64` | WSTG-INPV-01 | Base64 payload hiding |
| `utf7` | WSTG-INPV-01 | UTF-7 charset bypass |
| `overlong_utf8` | WSTG-INPV-01 | Overlong UTF-8 sequence bypass |

## References

- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [OWASP Web Security Testing Guide v4.2](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP ModSecurity Core Rule Set](https://coreruleset.org/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)
- [2026 WAF Comparison Project](https://blog.checkpoint.com/securing-the-cloud/waf-security-test-results-2026-why-prevention-first-matters-more-than-ever/)
