# Phase 1 — Python Nâng Cao (Must-know trước FastAPI)

**Thời gian:** 5-7 ngày
**Mục tiêu:** Hiểu type hints, OOP, async/await - nền tảng cần cho FastAPI.

## Tại sao phase này quan trọng?

FastAPI **dựa trên 3 thứ**:
1. **Type hints** → auto validation, auto doc
2. **Pydantic** (class) → data models
3. **async/await** → performance

Không nắm 3 thứ này → dùng FastAPI như copy-paste, không hiểu tại sao lỗi.

## Kế hoạch theo ngày

| Ngày | Chủ đề | File |
|------|--------|------|
| 1 | Type hints cơ bản | `01_type_hints.py` |
| 2 | Type hints nâng cao (Generic, Protocol, Annotated) | `02_type_advanced.py` |
| 3-4 | OOP cơ bản (class, instance, inheritance) | `03_oop.py` |
| 5 | Dataclass, Enum | `04_dataclass_enum.py` |
| 6 | Async/await, asyncio | `05_async.py` |
| 7 | Mini-project | `mini-project/` |

## Must-know: Type hints

Python không bắt buộc type hints, nhưng FastAPI **ĐỌC** type hints để:
- Validate request/response
- Generate OpenAPI docs tự động
- IDE autocomplete

So sánh:
```python
# ❌ Python thuần - không ai biết type gì
def get_user(id):
    return {"id": id, "name": "An"}

# ✅ Có type hints - FastAPI hiểu được
def get_user(id: int) -> dict[str, str | int]:
    return {"id": id, "name": "An"}
```

## Must-know: Async

```python
# Sync (blocking) - đợi xong mới làm tiếp
def fetch_data():
    response = requests.get(url)  # block 1 giây
    return response.json()

# Async (non-blocking) - nhường CPU làm việc khác khi đợi
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.json()
```

FastAPI endpoint có thể là `def` hoặc `async def`. Nhưng nếu I/O (DB, HTTP) → BẮT BUỘC async.

## Must-know: OOP ở mức vừa đủ

Không cần biết metaclass, descriptor. Chỉ cần:
- Tạo class, `__init__`
- Instance method vs class method vs static method
- Inheritance (vì Pydantic model kế thừa BaseModel)
- `@property`
- `@classmethod`

## Mini-project: Async Weather Fetcher

Viết script lấy thông tin thời tiết nhiều thành phố **song song** bằng async.

```bash
$ python weather.py HN SG DN NY TK
Hà Nội: 28°C, mưa nhẹ
Singapore: 32°C, nắng
...
(Fetched 5 cities in 1.2s — async)
(Sequential version would take ~5s)
```

Yêu cầu:
- Dùng `httpx.AsyncClient`
- Dùng `asyncio.gather` để fetch song song
- Dùng `dataclass` cho Weather
- Dùng type hints đầy đủ
- So sánh thời gian sync vs async

API miễn phí: [open-meteo.com](https://open-meteo.com/) (không cần key).

## Checklist trước Phase 2

- [ ] Viết được type hints cho function có `list[int]`, `dict[str, Any]`, `X | None`
- [ ] Hiểu Generic là gì (không cần tự viết, chỉ cần đọc hiểu)
- [ ] Tự viết được class có `__init__`, method, `@property`
- [ ] Biết khác nhau giữa `@classmethod` và `@staticmethod`
- [ ] Dùng dataclass thành thạo
- [ ] Hiểu `async def` khác `def` như nào
- [ ] Biết khi nào cần `await`
- [ ] Mini-project chạy ok, thời gian async < sync rõ rệt

→ [Phase 2: FastAPI Basics](../phase-2-fastapi-basics/PHASE.md)
