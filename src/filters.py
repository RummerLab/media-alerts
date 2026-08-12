from .config import EXCLUDED_HOST_SUFFIXES, RELEVANCE_PHRASES
from .models import Article
from .normalize import host_of


def is_own_site(url: str) -> bool:
    host = host_of(url)
    if not host:
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in EXCLUDED_HOST_SUFFIXES)


def is_relevant(article: Article) -> bool:
    if article.trusted:
        return True
    blob = " ".join(
        part
        for part in (article.title, article.snippet, article.source, article.url)
        if part
    ).lower()
    return any(phrase in blob for phrase in RELEVANCE_PHRASES)
