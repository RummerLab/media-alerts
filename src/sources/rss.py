from __future__ import annotations

import logging
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from time import mktime

import feedparser
import requests

from ..config import RSS_FEEDS, USER_AGENT
from ..models import Article
from ..normalize import canonicalize_url

logger = logging.getLogger(__name__)


def _entry_datetime(entry: object) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=UTC)
            except (OverflowError, OSError, TypeError, ValueError):
                pass
    for attr in ("published", "updated"):
        value = getattr(entry, attr, None)
        if not value:
            continue
        try:
            stamp = parsedate_to_datetime(str(value))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=UTC)
            return stamp.astimezone(UTC)
        except (TypeError, ValueError):
            continue
    return None


def _snippet(entry: object) -> str:
    summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
    return " ".join(str(summary).split())[:400]


def _source_name(entry: object, fallback: str) -> str:
    source = getattr(entry, "source", None)
    if source is not None:
        title = getattr(source, "title", "") or ""
        if title:
            return str(title)
    title = str(getattr(entry, "title", "") or "")
    if " - " in title:
        return title.rsplit(" - ", 1)[-1].strip() or fallback
    return fallback


def _clean_title(title: str, source: str) -> str:
    suffix = f" - {source}"
    if title.endswith(suffix):
        return title[: -len(suffix)].strip()
    return title.strip()


def _source_url(entry: object) -> str:
    source = getattr(entry, "source", None)
    if source is None:
        return ""
    href = getattr(source, "href", "") or ""
    if not href and hasattr(source, "get"):
        href = source.get("href") or source.get("url") or ""
    return canonicalize_url(str(href or ""))


def _primary_url(entry: object) -> tuple[str, list[str]]:
    rss_link = canonicalize_url(str(getattr(entry, "link", "") or ""))
    outlet_url = _source_url(entry)
    extra: list[str] = []
    if outlet_url and rss_link and outlet_url != rss_link:
        extra.append(rss_link)
        return outlet_url, extra
    return rss_link or outlet_url, extra


def fetch_feed(name: str, url: str, trusted: bool = False) -> list[Article]:
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("RSS fetch failed for %s: %s", name, exc)
        return []

    parsed = feedparser.parse(response.content)
    articles: list[Article] = []
    for entry in parsed.entries:
        link, extra = _primary_url(entry)
        if not link:
            continue
        source = _source_name(entry, name)
        title = _clean_title(str(getattr(entry, "title", "") or "Untitled"), source)
        published = _entry_datetime(entry)
        for link_obj in getattr(entry, "links", []) or []:
            href = ""
            if hasattr(link_obj, "get"):
                href = canonicalize_url(str(link_obj.get("href", "") or ""))
            if href and href != link and href not in extra:
                extra.append(href)
        articles.append(
            Article(
                title=title,
                url=link,
                source=source,
                snippet=_snippet(entry),
                published=published.isoformat() if published else "",
                feed=name,
                trusted=trusted,
                extra_urls=extra,
            )
        )
    logger.info("%s: %s entries", name, len(articles))
    return articles


def fetch_rss_articles() -> list[Article]:
    items: list[Article] = []
    for feed in RSS_FEEDS:
        items.extend(
            fetch_feed(
                str(feed["name"]),
                str(feed["url"]),
                bool(feed.get("trusted", False)),
            )
        )
    return items
