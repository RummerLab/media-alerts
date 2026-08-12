from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import requests

from ..config import LOOKBACK_DAYS, NEWS_API_ORG_KEY, QUERY, USER_AGENT
from ..models import Article
from ..normalize import canonicalize_url

logger = logging.getLogger(__name__)


def fetch_newsapi_articles() -> list[Article]:
    if not NEWS_API_ORG_KEY:
        logger.info("NewsAPI skipped (no NEWS_API_ORG_KEY)")
        return []

    since = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).date().isoformat()
    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": QUERY,
                "from": since,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 50,
                "apiKey": NEWS_API_ORG_KEY,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("NewsAPI failed: %s", exc)
        return []

    articles: list[Article] = []
    for item in payload.get("articles") or []:
        url = canonicalize_url(item.get("url") or "")
        if not url:
            continue
        source = ((item.get("source") or {}).get("name")) or "NewsAPI"
        articles.append(
            Article(
                title=item.get("title") or "Untitled",
                url=url,
                source=source,
                snippet=item.get("description") or "",
                published=item.get("publishedAt") or "",
                feed="NewsAPI",
            )
        )
    logger.info("NewsAPI: %s entries", len(articles))
    return articles
