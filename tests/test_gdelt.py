from unittest.mock import MagicMock, patch

import requests

from src.sources.gdelt import _normalize_seendate, _timespan, fetch_gdelt_articles


def test_timespan_maps_lookback_days() -> None:
    assert _timespan(7) == "7d"
    assert _timespan(0) == "1d"
    assert _timespan(120) == "90d"


def test_normalize_seendate() -> None:
    assert _normalize_seendate("20250303T105029Z") == "2025-03-03T10:50:29+00:00"
    assert _normalize_seendate("") == ""
    assert _normalize_seendate("not-a-date") == "not-a-date"


@patch("src.sources.gdelt.requests.get")
def test_gdelt_fetches_artlist(mock_get: MagicMock) -> None:
    mock_get.return_value = MagicMock(
        **{
            "text": '{"articles":[]}',
            "raise_for_status.return_value": None,
            "json.return_value": {
                "articles": [
                    {
                        "title": "Jodie Rummer: For the love of sharks",
                        "url": "https://oceanographicmagazine.com/features/jodie-rummer/",
                        "domain": "oceanographicmagazine.com",
                        "seendate": "20250303T105029Z",
                    }
                ]
            },
        }
    )

    articles = fetch_gdelt_articles()

    assert len(articles) == 1
    assert articles[0].feed == "GDELT"
    assert articles[0].source == "oceanographicmagazine.com"
    assert articles[0].published == "2025-03-03T10:50:29+00:00"
    assert mock_get.call_args.args[0] == "https://api.gdeltproject.org/api/v2/doc/doc"
    params = mock_get.call_args.kwargs["params"]
    assert params["mode"] == "ArtList"
    assert params["format"] == "json"
    assert "apiKey" not in params


@patch("src.sources.gdelt.requests.get")
def test_gdelt_returns_empty_on_failure(mock_get: MagicMock) -> None:
    mock_get.side_effect = requests.exceptions.ConnectionError("reset")
    assert fetch_gdelt_articles() == []
