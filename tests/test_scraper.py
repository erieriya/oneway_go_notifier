from unittest.mock import Mock, patch

import pytest
import requests

from src.scraper import fetch_html


def test_fetch_html_returns_text_on_success():
    response = Mock(status_code=200, text="<html>ok</html>", apparent_encoding="utf-8")
    response.raise_for_status = Mock()
    with patch("src.scraper.requests.get", return_value=response) as mock_get:
        result = fetch_html(retries=3, backoff_seconds=0)

    assert result == "<html>ok</html>"
    mock_get.assert_called_once()


def test_fetch_html_retries_then_succeeds():
    failing_response = Mock()
    failing_response.raise_for_status = Mock(
        side_effect=requests.exceptions.HTTPError("503 Server Error")
    )
    ok_response = Mock(text="<html>ok</html>", apparent_encoding="utf-8")
    ok_response.raise_for_status = Mock()

    with patch(
        "src.scraper.requests.get", side_effect=[failing_response, ok_response]
    ) as mock_get:
        result = fetch_html(retries=3, backoff_seconds=0)

    assert result == "<html>ok</html>"
    assert mock_get.call_count == 2


def test_fetch_html_raises_after_exhausting_retries():
    failing_response = Mock()
    failing_response.raise_for_status = Mock(
        side_effect=requests.exceptions.ReadTimeout("read timed out")
    )

    with patch("src.scraper.requests.get", return_value=failing_response) as mock_get:
        with pytest.raises(requests.exceptions.ReadTimeout):
            fetch_html(retries=3, backoff_seconds=0)

    assert mock_get.call_count == 3
