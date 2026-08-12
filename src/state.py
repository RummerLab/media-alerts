import json
from pathlib import Path

from .config import DATA_DIR, SEEN_PATH
from .models import Article
from .normalize import canonicalize_url


def load_seen() -> set[str]:
    path = Path(SEEN_PATH)
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if isinstance(payload, list):
        return {str(item) for item in payload}
    return set()


def save_seen(seen: set[str]) -> None:
    path = Path(SEEN_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(sorted(seen), indent=2) + "\n",
        encoding="utf-8",
    )


def article_keys(article: Article) -> set[str]:
    keys = {canonicalize_url(article.url)} if article.url else set()
    keys.update(canonicalize_url(url) for url in article.extra_urls if url)
    title_key = " ".join(article.title.lower().split())
    if title_key:
        keys.add(f"title:{title_key}")
    return {key for key in keys if key}


def unseen_articles(articles: list[Article], seen: set[str]) -> list[Article]:
    fresh: list[Article] = []
    claimed: set[str] = set()
    for article in articles:
        keys = article_keys(article)
        if keys & seen or keys & claimed:
            continue
        fresh.append(article)
        claimed.update(keys)
    return fresh


def mark_seen(articles: list[Article], seen: set[str]) -> set[str]:
    updated = set(seen)
    for article in articles:
        updated.update(article_keys(article))
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    return updated
