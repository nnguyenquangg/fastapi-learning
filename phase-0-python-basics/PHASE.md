# Phase 0 — Python Nền Tảng

**Thời gian:** 5-7 ngày
**Mục tiêu:** Đọc-viết Python thành thạo ở mức có thể tự giải bài tập nhỏ.

## Bạn sẽ học được gì

- Cú pháp Python: biến, kiểu, điều kiện, vòng lặp
- Data structures: list, dict, set, tuple
- Function, scope, `*args`/`**kwargs`
- File I/O
- Module & import
- Xử lý lỗi (try/except)
- Hiểu được traceback

## Bạn KHÔNG cần học ngay

- ❌ OOP nâng cao (metaclass, descriptor...)
- ❌ Async/await
- ❌ Decorator tự viết
- ❌ Type hints chi tiết

→ Phase 1 sẽ học.

## Kế hoạch theo ngày

| Ngày | Chủ đề | Exercise |
|------|--------|----------|
| 1 | Biến, kiểu dữ liệu, print/input | `01_basics.py` |
| 2 | List, dict, loop, if/else | `02_collections.py` |
| 3 | Function, scope | `03_functions.py` |
| 4 | File I/O, module | `04_files.py` |
| 5 | Try/except, debugging | `05_errors.py` |
| 6-7 | Mini-project | `mini-project/` |

## Tài liệu học

1. **Đọc từng phần rồi code liền** — đừng đọc hết rồi mới code
2. [Python Official Tutorial](https://docs.python.org/3/tutorial/) — chương 3-7
3. Video (tùy chọn): [Corey Schafer Python Basics](https://www.youtube.com/playlist?list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7)

## Mini-project: CLI Todo App

Viết một app todo lưu vào file `.json`. Chạy trong terminal:

```bash
$ python todo.py add "Học FastAPI"
Added: Học FastAPI (id=1)

$ python todo.py list
[1] ☐ Học FastAPI
[2] ☑ Đọc sách

$ python todo.py done 1
Marked done: Học FastAPI
```

Yêu cầu:
- Dùng `argparse` hoặc `sys.argv`
- Lưu/đọc file JSON
- Xử lý khi file chưa tồn tại
- Xử lý khi id không hợp lệ

→ Khi làm được mini-project = bạn đã qua Phase 0.

## Checklist trước khi sang Phase 1

- [ ] Đọc được code Python thuần không bị rối
- [ ] Tự viết function không cần google cú pháp
- [ ] Hiểu sự khác biệt giữa `list` và `tuple`, `dict` và `set`
- [ ] Biết đọc traceback và tìm được dòng bị lỗi
- [ ] Mini-project chạy không lỗi

→ Tất cả tick ✅ → qua [Phase 1](../phase-1-python-advanced/PHASE.md)
