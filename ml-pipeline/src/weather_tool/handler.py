import json
import urllib.error
import urllib.parse
import urllib.request


def get_weather_data(city: str) -> dict:
    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise ValueError(f"Weather service returned HTTP {exc.code} for '{city}'") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"Could not reach weather service: {exc.reason}") from exc

    try:
        current = data["current_condition"][0]
        return {
            "city": data["nearest_area"][0]["areaName"][0]["value"],
            "temperature_c": int(current["temp_C"]),
            "temperature_f": int(current["temp_F"]),
            "condition": current["weatherDesc"][0]["value"].strip(),
            "humidity_percent": int(current["humidity"]),
            "wind_kph": int(current["windspeedKmph"]),
        }
    except (KeyError, IndexError) as exc:
        raise ValueError(f"Unexpected response format from weather service: {exc}") from exc


def lambda_handler(event, context):
    city = (event.get("city") or "").strip()
    if not city:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "city parameter is required and must be a non-empty string",
                }
            ]
        }

    try:
        weather = get_weather_data(city)
        return {"content": [{"type": "text", "text": json.dumps(weather)}]}
    except ValueError as exc:
        return {"content": [{"type": "text", "text": str(exc)}]}
