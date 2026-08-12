from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import requests

from ..config import GUARDIAN_API_KEY, LOOKBACK_DAYS, QUERY, USER_AGENT
from ..models import Article
from ..normalize import canonicalize_url

logger = logging.getLogger(__name__)


def fetch_guardian_articles() -> list[Article]:
    if not GUARDIAN_API_KEY:
        logger.info("Guardian API skipped (no THE_GUARDIAN_API_KEY)")
        return []

    since = (datetime.now(UTC) - timedelta(days=LOOKBACK_DAYS)).date().isoformat()
    try:
        response = requests.get(
            "https://content.guardianapis.com/search",
            params={
                "q": QUERY,
                "from-date": since,
                "order-by": "newest",
                "page-size": 50,
                "show-fields": "headline,trailText,bodyText",
                "api-key": GUARDIAN_API_KEY,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Guardian API failed: %s", exc)
        return []

    results = payload.get("response", {}).get("results", [])
    articles: list[Article] = []
    for item in results:
        fields = item.get("fields") or {}
        url = canonicalize_url(item.get("webUrl", ""))
        if not url:
            continue
        articles.append(
            Article(
                title=fields.get("headline") or item.get("webTitle") or "Untitled",
                url=url,
                source="The Guardian",
                snippet=fields.get("trailText") or "",
                published=item.get("webPublicationDate", ""),
                feed="Guardian API",
            )
        )
    logger.info("Guardian API: %s entries", len(articles))
    return articles
