import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict, dataclass, replace

import httpx

from api import CityNotFoundError, WeatherAPIError, get_city_weather
from models import Weather


@dataclass(frozen=True)
class CityResult:
    query: str
    weather: Weather | None
    error: str | None
    elapsed: float


async def fetch_city(client: httpx.AsyncClient, city: str) -> CityResult:
    start = time.perf_counter()
    try:
        weather = await get_city_weather(client, city)
        return CityResult(city, weather, None, time.perf_counter() - start)
    except CityNotFoundError:
        return CityResult(city, None, "Not found", time.perf_counter() - start)
    except WeatherAPIError as e:
        return CityResult(city, None, f"Error: {e}", time.perf_counter() - start)


async def fetch_all(cities: list[str], timeout: float) -> list[CityResult]:
    async with httpx.AsyncClient(timeout=timeout) as client:
        return list(await asyncio.gather(*(fetch_city(client, c) for c in cities)))


def render_text(results: list[CityResult], total: float) -> str:
    bar = "━" * 44
    width = max(len(r.query) for r in results)
    lines = [bar]
    for r in results:
        if r.weather is not None:
            shown = replace(r.weather, location=replace(r.weather.location, name=r.query))
            lines.append(shown.format(width))
        else:
            lines.append(f"{r.query:<{width}}: {r.error}")
    lines.append(bar)
    failed = sum(1 for r in results if r.weather is None)
    summary = f"Fetched {len(results)} cities in {total:.2f}s (async)"
    if failed:
        summary += f" — {failed} failed"
    lines.append(summary)
    lines.append(f"Sequential would take ~{sum(r.elapsed for r in results):.2f}s")
    return "\n".join(lines)


def render_json(results: list[CityResult], total: float) -> str:
    payload = {
        "results": [
            {
                "query": r.query,
                "weather": asdict(r.weather) if r.weather else None,
                "error": r.error,
            }
            for r in results
        ],
        "async_seconds": round(total, 3),
        "sequential_estimate_seconds": round(sum(r.elapsed for r in results), 3),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Async weather fetcher (Open-Meteo)")
    parser.add_argument("cities", nargs="+", help="City names")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout (s)")
    args = parser.parse_args(argv)

    start = time.perf_counter()
    results = asyncio.run(fetch_all(args.cities, args.timeout))
    total = time.perf_counter() - start

    print(render_json(results, total) if args.json else render_text(results, total))
    return 0 if any(r.weather for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())