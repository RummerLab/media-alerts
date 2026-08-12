from src.filters import is_own_site, is_relevant
from src.models import Article


def test_own_sites_are_excluded():
    assert is_own_site("https://rummerlab.com/media")
    assert is_own_site("https://www.physioshark.org/about")
    assert not is_own_site("https://www.theguardian.com/environment/example")


def test_relevance_requires_lab_or_name():
    hit = Article(
        title="Shark cull will not improve beach safety",
        url="https://www.abc.net.au/news/example",
        source="ABC News",
        snippet="Jodie Rummer said culling does not work.",
    )
    miss = Article(
        title="Townsville weather",
        url="https://www.abc.net.au/news/weather",
        source="ABC News",
        snippet="A fine weekend is expected.",
    )
    assert is_relevant(hit)
    assert not is_relevant(miss)


def test_trusted_conversation_feed_is_kept():
    article = Article(
        title="How fish can still be part of a more sustainable food future",
        url="https://theconversation.com/example",
        source="The Conversation",
        trusted=True,
    )
    assert is_relevant(article)
