"""
Exercise 05 — Async / Await

Foundation cho FastAPI. Hiểu rõ trước khi làm API.

Install: uv add httpx
"""
import asyncio
import time
import requests

# --- Concept: Sync vs Async ---
#
# Sync (blocking):
#   def fetch():
#       time.sleep(1)          # CPU đứng chờ 1 giây, không làm gì khác
#       return "done"
#
# Async (non-blocking):
#   async def fetch():
#       await asyncio.sleep(1) # CPU có thể chạy task khác trong 1 giây
#       return "done"
#
# Key: await chỉ dùng được TRONG async function


# --- Bài 1: First async function ---
# async def hello():
#     print("start")
#     await asyncio.sleep(1)
#     print("end")
#     return "ok"
#
# Chạy bằng: asyncio.run(hello())
# TODO: viết và chạy
# result = asyncio.run(hello())
# print(result)
# start
# chờ 1 giây
# end 
# ok


# --- Bài 2: Sequential vs Concurrent ---
# Sequential (tuần tự):
# async def seq():
#     await task_a()   # xong mới tới
#     await task_b()   # xong mới tới
#     await task_c()
# Nếu mỗi task 1s → tổng 3s
#
# Concurrent (song song):
# async def concur():
#     await asyncio.gather(task_a(), task_b(), task_c())
# Nếu mỗi task 1s → tổng ~1s (chạy song song)
#
# TODO: viết 3 task mỗi task sleep 1s rồi return f"task {n}"
# So sánh thời gian sequential vs gather

async def task(n):
    await asyncio.sleep(1)
    return f"task {n}"

async def sequential():
    start = time.perf_counter()

    task1 = await task(1)
    task2 = await task(1)
    task3 = await task(1)

    e = time.perf_counter() - start
    print("Sequential:", [task1, task2, task3], f"- {e:.2f}s")

async def concur():
    start = time.perf_counter()

    results = await asyncio.gather(task(1), task(2), task(3))

    e = time.perf_counter() - start
    print("Concurrent:", results, f"- {e:.2f}s")

async def main2():
    await sequential()
    await concur()


# asyncio.run(main2())

# --- Bài 3: asyncio.gather ---
async def fetch_user(user_id: int) -> dict:
    """Giả lập gọi API lấy user."""
    await asyncio.sleep(0.5)
    return {"id": user_id, "name": f"User {user_id}"}

# TODO: viết function fetch_many(ids: list[int]) dùng gather
# So sánh với version dùng for loop tuần tự
async def fetch_many_sequential(ids: list[int]) -> list[dict]:
    results = []
    for user_id in ids:
        user = await fetch_user(user_id) #chờ chạy xong mới lấy user
        results.append(user)
    return results

async def fetch_many(ids: list[int]) -> list[dict]:
    tasks = []
    for user_id in ids:
        tasks.append(fetch_user(user_id))
    results = await asyncio.gather(*tasks)
    return results

async def main3():
    ids = [1, 2, 3, 4, 5]
    start = time.perf_counter()
    await fetch_many_sequential(ids)
    print("Tuần tự:", round(time.perf_counter() - start, 1), "giây")

    start = time.perf_counter()
    await fetch_many(ids)
    print("Gather:", round(time.perf_counter() - start, 1), "giây")

# asyncio.run(main3())


# --- Bài 4: Timeout ---
# Dùng asyncio.wait_for để giới hạn thời gian:
# try:
#     result = await asyncio.wait_for(slow_task(), timeout=2.0)
# except asyncio.TimeoutError:
#     print("Too slow!")
# TODO: viết slow_task sleep 3s, gọi với timeout 1s, bắt exception

async def slow_task():
    await asyncio.sleep(3)
    return "done"

async def main4():
    start = time.perf_counter()
    try:
        result = await asyncio.wait_for(slow_task(), timeout=1.0)
        print("Kết quả: ", result)
    except asyncio.TimeoutError:
        print("Too slow!")
    print("Thời gian chờ:", round(time.perf_counter() - start, 1), "giây"), 

# asyncio.run(main4())

# --- Bài 5: Real HTTP với httpx ---
import httpx

async def get_post(post_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
        r.raise_for_status()
        return r.json()
# TODO: fetch 10 post ids song song, in title của mỗi post

async def main5():
    ids = list(range(1, 11))

    tasks = []
    for post_id in ids:
        tasks.append(get_post(post_id))
    posts = await asyncio.gather(*tasks)

    for post in posts:
        print(post["id"], "-", post["title"])

# asyncio.run(main5())

# --- Bài 6: Async context manager ---
# `async with`  dùng khi resource cần acquire/release async
# (database connection, HTTP client, file async...)
# Ví dụ:
# async with httpx.AsyncClient() as client:
#     ...
# Không cần viết manager riêng, chỉ cần biết khi nào dùng
async def main6():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://jsonplaceholder.typicode.com/posts/1")
        print(res.json())
        print(res.json()["title"])

# asyncio.run(main6())


# --- Bài 7: Async iteration ---
# `async for` với async generator
async def stream_numbers():
    for i in range(5):
        await asyncio.sleep(0.2)
        yield i

# async for n in stream_numbers():
#     print(n)
# TODO: viết async generator rồi consume
async def main7():
    async for n in stream_numbers():
        print(n)

# asyncio.run(main7())


# --- Bài 8: Khi nào KHÔNG dùng async? ---
# - CPU-intensive (tính toán nặng) → dùng multiprocessing
# - Dùng thư viện sync (vd: psycopg2 sync) → gọi bằng asyncio.to_thread
#
# Ví dụ:
# def heavy_compute(x):   # sync, chạy 2 giây
#     ...
# async def main():
#     result = await asyncio.to_thread(heavy_compute, 10)
#     # chạy trong thread pool, không block event loop


# --- Bài 9: Lỗi thường gặp ---
# ❌ Quên await:
#   result = fetch_user(1)     # trả về coroutine object, KHÔNG phải data
#   result = await fetch_user(1)  # ✅
#
# ❌ Gọi async function trong sync:
#   def main():
#       fetch_user(1)   # không chạy!
#   → cần: asyncio.run(fetch_user(1))
#
# ❌ Trộn sync I/O trong async endpoint:
#   async def handler():
#       time.sleep(5)           # ❌ block toàn event loop
#       await asyncio.sleep(5)  # ✅


# --- Bài 10: Benchmark ---
# Viết 2 version lấy 20 user:
# - Sync (dùng requests, time.sleep)
# - Async (dùng httpx, asyncio.sleep + gather)
# Đo thời gian bằng time.perf_counter()
# Print ra sự khác biệt
# TODO:

URL = "https://jsonplaceholder.typicode.com/users/{}"
listUser = list(range(1, 21))

# Dùng Sync
def fetch_sync():
    results = []
    for user_id in listUser:
        res = requests.get(URL.format(user_id))
        results.append(res.json())
    return results

# Dùng Async
async def fetch_one(client, user_id):
    res = await client.get(URL.format(user_id))
    return res.json

async def fetch_async():
    async with httpx.AsyncClient() as client:
        tasks = []
        for user_id in listUser:
            tasks.append(fetch_one(client, user_id))
        return await asyncio.gather(*tasks)
    
# Đo thời gian
start = time.perf_counter()
fetch_sync()
sync_time = time.perf_counter() - start

start = time.perf_counter()
asyncio.run(fetch_async())
async_time = time.perf_counter() - start

print(f"Sync: {sync_time:.2f} giây")
print(f"Async: {async_time:.2f} giây")