FROM python:3.14-slim AS builder

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.14-slim

LABEL org.opencontainers.image.title="subdomain-enum"
LABEL org.opencontainers.image.description="CLI утилита для поиска поддоменов"
LABEL org.opencontainers.image.version="0.1.0"

WORKDIR /app

COPY --from=builder /install /usr/local

COPY wordlists/ ./wordlists/

RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app

USER appuser

ENTRYPOINT [ "subdomain-enum" ]

CMD [ "--help" ]