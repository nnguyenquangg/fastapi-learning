from typing  import Any
import httpx
from models import Location, Weather

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

class CityNotFoundError(Exception):
    """Geocoding trả về 0 kết quả."""

class WeatherAPIError(Exception):
    """Lỗi network / HTTP / dữ liệu trả về không hợp lệ."""

async def _get_json(client: httpx.AsyncClient, url: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    except httpx.TimeoutException as e:
        raise WeatherAPIError("timeout") from e
    except httpx.HTTPStatusError as e:
        raise WeatherAPIError(f"HWTTO {e.response.status_code}") from e
    except ValueError as e:
        raise WeatherAPIError("invalid JSON response") from e
    if not isinstance(data, dict):
        raise WeatherAPIError("unexpected response shape")
    return data

async def geocode(client: httpx.AsyncClient, city: str) -> Location:
    data = await _get_json(client, GEOCODING_URL, {"name": city, "count": 1})
    results = data.get("results")
    if not results:
        raise CityNotFoundError(city)
    try:
        r = results[0]
        return Location(
            name=str(r["name"]),
            latitude=float(r["latitude"]),
            longitude=float(r["longitude"]),
            country=str(r["country"])
        )
    except (KeyError, TypeError, ValueError) as e:
        raise WeatherAPIError("invalid geocoding data") from e

async def fetch_weather(client: httpx.AsyncClient, location: Location) -> Weather:
    data = await _get_json(
        client,
        FORECAST_URL,
        {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "wind_speed_unit": "ms"
        }
    )
    try:
        cur = data["current"]
        return Weather(
            location=location,
            temperature=float(cur["temperature_2m"]),
            humidity=int(cur["relative_humidity_2m"]),
            wind_speed=float(cur["wind_speed_10m"])
        )
    except (KeyError, TypeError, ValueError) as e:
        raise WeatherAPIError("invalid weather data") from e
    
async def get_city_weather(client: httpx.AsyncClient, city: str) -> Weather:
    """Geocoding rồi weather — tuần tự trong 1 city."""
    location = await geocode(client, city)
    return await fetch_weather(client, location)