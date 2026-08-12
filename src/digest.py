from __future__ import annotations

import argparse
import logging
import time
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from .config import DIGEST_HOUR, DIGEST_MINUTE, LOOKBACK_DAYS, RUN_ON_START
from .emailer import send_digest
from .filters import is_own_site, is_relevant
from .models import Article
from .sources import fetch_guardian_articles, fetch_newsapi_articles, fetch_rss_articles
from .state import load_seen, mark_seen, save_seen, unseen_articles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _parse_published(value: str) -> datetime | None:
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=UTC)
        return stamp.astimezone(UTC)
    except ValueError:
        return None


def collect_articles() -> list[Article]:
    items = [
        *fetch_rss_articles(),
        *fetch_guardian_articles(),
        *fetch_newsapi_articles(),
    ]
    cutoff = datetime.now(UTC) - timedelta(days=LOOKBACK_DAYS)
    kept: list[Article] = []
    for article in items:
        if is_own_site(article.url):
            continue
        if not is_relevant(article):
            continue
        published = _parse_published(article.published)
        if published and published < cutoff:
            continue
        kept.append(article)
    return kept


def run_once() -> int:
    articles = collect_articles()
    seen = load_seen()
    fresh = unseen_articles(articles, seen)
    logger.info("Fetched %s relevant items, %s new", len(articles), len(fresh))
    if not fresh:
        save_seen(mark_seen(articles, seen))
        logger.info("No new items; email not sent")
        return 0
    send_digest(fresh)
    save_seen(mark_seen(articles, seen))
    return len(fresh)


def _seconds_until_next_run() -> float:
    tz = ZoneInfo("Australia/Brisbane")
    now = datetime.now(tz)
    target = now.replace(hour=DIGEST_HOUR, minute=DIGEST_MINUTE, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return max(1.0, (target - now).total_seconds())


def run_schedule() -> int:
    if RUN_ON_START:
        run_once()
    while True:
        wait = _seconds_until_next_run()
        logger.info("Sleeping %.0f seconds until next digest", wait)
        time.sleep(wait)
        try:
            run_once()
        except Exception:
            logger.exception("Digest run failed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RummerLab media digest")
    parser.add_argument("--once", action="store_true", help="Run one digest and exit")
    parser.add_argument("--schedule", action="store_true", help="Run daily at DIGEST_HOUR")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and print new items without sending email",
    )
    args = parser.parse_args(argv)

    if args.dry_run:
        articles = unseen_articles(collect_articles(), load_seen())
        for article in articles:
            print(f"{article.source}\t{article.title}\t{article.url}")
        print(f"{len(articles)} new item(s)")
        return 0
    if args.once:
        run_once()
        return 0
    return run_schedule()
