# Docker Examples

The `examples/` directory contains Docker Compose setups for testing wafworth against different WAFs.

## ModSecurity + Nginx

```bash
cd examples/modsecurity-nginx
docker compose up -d
wafworth run --target http://localhost:8080 --name modsecurity
```

Uses the official [OWASP ModSecurity CRS](https://hub.docker.com/r/owasp/modsecurity-crs) image with Nginx. Configuration:

- **PARANOIA**: CRS paranoia level (default: 1)
- **ANOMALY_INBOUND**: Inbound anomaly score threshold (default: 5)

The compose file includes a backend Nginx container and a ModSecurity reverse proxy.

## Coraza + Caddy

```bash
cd examples/coraza-caddy
docker compose up -d
wafworth run --target http://localhost:8080 --name coraza
```

Uses Caddy with the Coraza WAF plugin. The Caddyfile configures Coraza as a request filter in front of the backend.

## Zentinel

```bash
cd examples/zentinel
docker compose up -d
wafworth run --target http://localhost:8080 --name zentinel
```

Uses the Zentinel proxy with a KDL configuration file. The compose file pulls from `ghcr.io/zentinelproxy/zentinel:latest`.

## Multi-WAF Comparison

Run all three and compare:

```bash
# Start all WAFs (adjust ports to avoid conflicts)
cd examples/modsecurity-nginx && docker compose up -d
cd ../coraza-caddy && docker compose -p coraza up -d  # uses different project name
cd ../zentinel && docker compose -p zentinel up -d

# Run tests against each
wafworth run -t http://localhost:8080 -n modsecurity -o results/modsec/
wafworth run -t http://localhost:8081 -n coraza -o results/coraza/
wafworth run -t http://localhost:8082 -n zentinel -o results/zentinel/

# Compare
wafworth compare -r results/modsec/ -r results/coraza/ -r results/zentinel/
```

## Building wafworth as a Container

```bash
docker build -t wafworth .
docker run --rm wafworth run --target http://host.docker.internal:8080 --name my-waf
```
