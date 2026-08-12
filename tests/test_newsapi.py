from unittest.mock import MagicMock, patch

from src.sources.newsapi import fetch_newsapi_articles


@patch("src.sources.newsapi.NEWS_API_ORG_KEY", "test-key")
@patch("src.sources.newsapi.requests.get")
def test_newsapi_uses_top_headlines_endpoint(mock_get: MagicMock) -> None:
    mock_get.return_value = MagicMock(
        **{
            "raise_for_status.return_value": None,
            "json.return_value": {
                "status": "ok",
                "articles": [
                    {
                        "title": "Jodie Rummer on reef sharks",
                        "url": "https://example.com/story",
                        "description": "Lab research",
                        "publishedAt": "2026-08-12T01:00:00Z",
                        "source": {"name": "Example News"},
                    }
                ],
            },
        }
    )

    articles = fetch_newsapi_articles()

    assert len(articles) == 1
    assert articles[0].title.startswith("Jodie Rummer")
    assert articles[0].feed == "NewsAPI"
    url = mock_get.call_args.args[0]
    params = mock_get.call_args.kwargs["params"]
    assert url == "https://newsapi.org/v2/top-headlines"
    assert "from" not in params
    assert params["pageSize"] == 100


@patch("src.sources.newsapi.NEWS_API_ORG_KEY", "")
def test_newsapi_skips_without_key() -> None:
    assert fetch_newsapi_articles() == []
