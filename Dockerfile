FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY testcases/ testcases/

RUN pip install --no-cache-dir .

ENTRYPOINT ["wafworth"]
