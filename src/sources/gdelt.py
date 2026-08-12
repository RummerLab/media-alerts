from __future__ import annotations

import logging
from datetime import UTC, datetime

import requests

from ..config import LOOKBACK_DAYS, QUERY, USER_AGENT
from ..models import Article
from ..normalize import canonicalize_url

logger = logging.getLogger(__name__)

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


def _timespan(days: int) -> str:
    """Map lookback days to a GDELT DOC timespan value."""
    capped = max(1, min(days, 90))
    return f"{capped}d"


def _normalize_seendate(value: str) -> str:
    """Convert GDELT seendate (YYYYMMDDTHHMMSSZ) to ISO-8601 UTC."""
    if not value:
        return ""
    try:
        stamp = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError:
        return value
    return stamp.isoformat()


def fetch_gdelt_articles() -> list[Article]:
    """Fetch matching articles from the free GDELT DOC 2.0 API (no key required)."""
    try:
        response = requests.get(
            GDELT_DOC_URL,
            params={
                "query": QUERY,
                "mode": "ArtList",
                "maxrecords": 250,
                "timespan": _timespan(LOOKBACK_DAYS),
                "format": "json",
                "sort": "DateDesc",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=45,
        )
        response.raise_for_status()
        if not response.text.strip():
            logger.info("GDELT: 0 entries (empty response)")
            return []
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("GDELT failed: %s", exc)
        return []

    articles: list[Article] = []
    for item in payload.get("articles") or []:
        url = canonicalize_url(item.get("url") or "")
        if not url:
            continue
        domain = (item.get("domain") or "").strip() or "GDELT"
        articles.append(
            Article(
                title=item.get("title") or "Untitled",
                url=url,
                source=domain,
                snippet="",
                published=_normalize_seendate(item.get("seendate") or ""),
                feed="GDELT",
            )
        )
    logger.info("GDELT: %s entries", len(articles))
    return articles
