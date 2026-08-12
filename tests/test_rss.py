from src.sources.rss import _clean_title, _primary_url


class _Source:
    def __init__(self, title: str, href: str):
        self.title = title
        self.href = href


class _Entry:
    def __init__(self, link: str, source: _Source | None = None):
        self.link = link
        self.source = source


def test_prefers_outlet_url_over_google_news_wrapper():
    entry = _Entry(
        link="https://news.google.com/rss/articles/CBMiEXAMPLE",
        source=_Source("ABC News", "https://www.abc.net.au/news/story?utm_source=rss"),
    )
    url, extra = _primary_url(entry)
    assert url == "https://www.abc.net.au/news/story"
    assert extra == ["https://news.google.com/rss/articles/CBMiEXAMPLE"]


def test_strips_outlet_suffix_from_title():
    assert _clean_title("Sharks on the reef - ABC News", "ABC News") == "Sharks on the reef"
