import json
import sys
import urllib.error
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "weather_tool"))
import handler  # noqa: E402

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "wttr_london_response.json").read_text()
)


class _FakeResponse:
    def __init__(self, data):
        self._body = json.dumps(data).encode()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


def test_valid_city_returns_weather_fields():
    with patch("urllib.request.urlopen", return_value=_FakeResponse(FIXTURE)):
        result = handler.lambda_handler({"city": "London"}, None)

    assert "content" in result
    assert result["content"][0]["type"] == "text"
    data = json.loads(result["content"][0]["text"])
    for key in ("city", "temperature_c", "temperature_f", "condition", "humidity_percent", "wind_kph"):
        assert key in data, f"Missing key: {key}"
    assert data["temperature_c"] == 30
    assert data["temperature_f"] == 87
    assert data["humidity_percent"] == 46
    assert data["condition"] == "Partly Cloudy"


def test_missing_city_returns_error_content():
    result = handler.lambda_handler({}, None)
    assert "content" in result
    assert "city" in result["content"][0]["text"].lower()


def test_empty_city_returns_error_content():
    result = handler.lambda_handler({"city": ""}, None)
    assert "content" in result
    assert "city" in result["content"][0]["text"].lower()


def test_whitespace_only_city_returns_error_content():
    result = handler.lambda_handler({"city": "   "}, None)
    assert "content" in result
    assert "city" in result["content"][0]["text"].lower()


def test_wttr_http_error_returns_error_content():
    err = urllib.error.HTTPError(
        url="https://wttr.in/badcity",
        code=404,
        msg="Not Found",
        hdrs=None,
        fp=BytesIO(b""),
    )
    with patch("urllib.request.urlopen", side_effect=err):
        result = handler.lambda_handler({"city": "badcity"}, None)

    assert "content" in result
    assert result["content"][0]["type"] == "text"
    assert "404" in result["content"][0]["text"]


def test_wttr_url_error_returns_error_content():
    err = urllib.error.URLError(reason="Name or service not known")
    with patch("urllib.request.urlopen", side_effect=err):
        result = handler.lambda_handler({"city": "somewhere"}, None)

    assert "content" in result
    assert result["content"][0]["type"] == "text"
