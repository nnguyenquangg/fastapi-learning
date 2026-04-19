# Mini-project: Async Weather Fetcher

**Mục tiêu:** Tổng hợp type hints + dataclass + async trong 1 tool.

## Yêu cầu

```bash
$ python weather.py Hanoi Singapore Tokyo "New York"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hanoi      : 28°C, humidity 78%, wind 2.1 m/s
Singapore  : 32°C, humidity 85%, wind 1.5 m/s
Tokyo      : 18°C, humidity 60%, wind 3.0 m/s
New York   : 12°C, humidity 55%, wind 4.2 m/s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fetched 4 cities in 0.82s (async)
Sequential would take ~3.20s
```

## API

Dùng [Open-Meteo](https://open-meteo.com/) — không cần key.
1. Geocoding: `https://geocoding-api.open-meteo.com/v1/search?name=<city>`
2. Weather: `https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&current=temperature_2m,relative_humidity_2m,wind_speed_10m`

## Yêu cầu kỹ thuật

- ✅ Dùng `httpx.AsyncClient`
- ✅ Dùng `asyncio.gather` - tất cả city fetch song song
- ✅ Mỗi city cần 2 request (geocoding + weather) → có thể gop sequential per-city, các city vẫn fetch song song
- ✅ Dùng `@dataclass` cho `Weather` và `Location`
- ✅ Full type hints, pass mypy strict
- ✅ Xử lý city không tìm thấy → in "Not found"
- ✅ Xử lý lỗi network (timeout, 500) - không crash, in error cho city đó
- ✅ Benchmark: đo thời gian async, tính ước lượng sequential

## Cấu trúc đề xuất

```
mini-project/
├── weather.py         # entry point
├── api.py             # async functions gọi API
├── models.py          # dataclass Weather, Location
└── pyproject.toml     # httpx dependency
```

## Setup

```bash
cd mini-project
uv init
uv add httpx
uv add --dev mypy ruff
```

## Template `models.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    country: str

@dataclass(frozen=True)
class Weather:
    location: Location
    temperature: float
    humidity: int
    wind_speed: float

    def format(self) -> str:
        return (
            f"{self.location.name:<11}: "
            f"{self.temperature:.0f}°C, "
            f"humidity {self.humidity}%, "
            f"wind {self.wind_speed:.1f} m/s"
        )
```

## Checklist

- [ ] Chạy đúng cho nhiều city (thử ít nhất 5)
- [ ] Async nhanh hơn sync có thể đo được
- [ ] Xử lý city sai tên (gõ sai → "Not found", không crash)
- [ ] Xử lý mất mạng (tắt wifi test → báo lỗi thân thiện)
- [ ] `mypy --strict weather.py` pass
- [ ] Đã tách module rõ ràng

## Bonus

- `--json` xuất ra JSON thay vì text
- `--format table` dùng `rich.Table`
- Cache kết quả geocoding vào file (tránh gọi API lặp)

Xong → [Phase 2: FastAPI Basics](../../phase-2-fastapi-basics/PHASE.md) 🚀
