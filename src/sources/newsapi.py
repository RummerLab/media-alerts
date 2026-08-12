from __future__ import annotations

import logging

import requests

from ..config import NEWS_API_ORG_KEY, QUERY, USER_AGENT
from ..models import Article
from ..normalize import canonicalize_url

logger = logging.getLogger(__name__)


def fetch_newsapi_articles() -> list[Article]:
    """Fetch matching items from NewsAPI.org free-tier `/v2/top-headlines`.

    The Developer plan returns 426 on `/v2/everything`; top-headlines is the
    free-compatible search surface (keyword match within current headlines).
    """
    if not NEWS_API_ORG_KEY:
        logger.info("NewsAPI skipped (no NEWS_API_ORG_KEY)")
        return []

    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "q": QUERY,
                "pageSize": 100,
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
