# syntax=docker/dockerfile:1

FROM python:3.12.16-alpine3.24 AS build

WORKDIR /src

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --no-compile -r requirements.txt

FROM python:3.12.16-alpine3.24 AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Australia/Brisbane \
    PATH="/opt/venv/bin:$PATH"

RUN --mount=type=cache,target=/etc/apk/cache,sharing=locked \
    apk add tzdata \
    && addgroup -S -g 1001 appgroup \
    && adduser -S -u 1001 -G appgroup appuser \
    && mkdir -p /app/data \
    && chown appuser:appgroup /app/data

COPY --from=build --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup src ./src

USER appuser

CMD ["python", "-m", "src", "--schedule"]
