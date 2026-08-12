from src.models import Article
from src.normalize import canonicalize_url, unwrap_google_url
from src.state import article_keys, unseen_articles


def test_unwraps_google_redirect():
    wrapped = "https://www.google.com/url?q=https://www.abc.net.au/news/story&sa=D"
    assert unwrap_google_url(wrapped) == "https://www.abc.net.au/news/story"


def test_strips_utm():
    url = "https://www.theguardian.com/environment/story?utm_source=rss&utm_medium=feed"
    assert canonicalize_url(url) == "https://www.theguardian.com/environment/story"


def test_dedupes_same_story_from_two_feeds():
    first = Article(
        title="Walking sharks",
        url="https://oceanographicmagazine.com/features/walking-sharks/",
        source="Oceanographic Magazine",
        feed="Google News AU",
    )
    second = Article(
        title="Walking sharks",
        url="https://oceanographicmagazine.com/features/walking-sharks/?utm_source=bing",
        source="Oceanographic Magazine",
        feed="Bing News",
    )
    fresh = unseen_articles([first, second], set())
    assert len(fresh) == 1
    assert article_keys(first) & article_keys(second)
