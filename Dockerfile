# syntax=docker/dockerfile:1

FROM python:3.15.0-alpine3.24 AS build

WORKDIR /src

COPY --from=ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 /uv /usr/local/bin/uv

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN --mount=type=bind,source=requirements.lock,target=requirements.lock \
    uv pip install --python /opt/venv/bin/python --require-hashes --exclude-newer 3d -r requirements.lock

FROM python:3.15.0-alpine3.24 AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Australia/Brisbane \
    PATH="/opt/venv/bin:$PATH"

# uid/gid 1000 matches the usual first host user, so the ./data bind mount stays
# writable; compose can override it via APP_UID/APP_GID when the host differs.
RUN --mount=type=cache,target=/etc/apk/cache,sharing=locked \
    apk add tzdata \
    && addgroup -S -g 1000 appgroup \
    && adduser -S -u 1000 -G appgroup appuser \
    && mkdir -p /app/data \
    && chown appuser:appgroup /app/data

COPY --from=build --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup src ./src

USER appuser

CMD ["python", "-m", "src", "--schedule"]
