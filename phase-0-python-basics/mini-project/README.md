# Mini-project: CLI Todo App

**Mục tiêu:** Dùng những gì đã học từ Phase 0 để build một app thực tế.

## Yêu cầu chức năng

```bash
$ python todo.py add "Học FastAPI"
Added [#1]: Học FastAPI

$ python todo.py add "Đọc sách" --priority high
Added [#2]: Đọc sách (high)

$ python todo.py list
[1] ☐ Học FastAPI (normal)
[2] ☐ Đọc sách (high)

$ python todo.py done 1
Marked done: Học FastAPI

$ python todo.py list --status done
[1] ☑ Học FastAPI (normal)

$ python todo.py delete 2
Deleted: Đọc sách

$ python todo.py clear --done
Cleared 1 done items
```

## Yêu cầu kỹ thuật

- ✅ Dùng `argparse` (subcommand)
- ✅ Lưu vào file `todos.json`
- ✅ Mỗi task có: `id`, `title`, `priority` (low/normal/high), `status` (pending/done), `created_at`
- ✅ Xử lý file chưa tồn tại
- ✅ Xử lý id không hợp lệ (in lỗi thân thiện, không crash)
- ✅ Module hóa: tách `storage.py` (đọc/ghi file) và `todo.py` (CLI)

## Cấu trúc đề xuất

```
mini-project/
├── todo.py          # CLI entrypoint
├── storage.py       # Load/save JSON
├── models.py        # (optional) kiểu dữ liệu task
└── todos.json       # auto-generate khi chạy
```

## Bonus (nếu dư thời gian)

- `--due` để thêm deadline, list sort theo due
- `search <keyword>` tìm task
- Màu sắc trong terminal (dùng `rich` hoặc escape codes)
- Xuất ra Markdown: `todo.py export > todos.md`

## Checklist hoàn thành

- [ ] App chạy không lỗi cho các lệnh cơ bản
- [ ] File JSON đọc/ghi đúng
- [ ] Khi xoá `todos.json`, chạy lại vẫn OK
- [ ] Đã viết docstring cho từng function
- [ ] Đã test các edge case (id âm, id quá lớn, title rỗng)
- [ ] Code đã chia module rõ ràng

## Tips khi stuck

1. **Bắt đầu từ `add` và `list`** - đơn giản nhất
2. **Print nhiều** - xem dữ liệu trông như nào trước khi refactor
3. **Commit sau mỗi command hoạt động** - giữ được state hoạt động

Xong → quay lại [PHASE.md](../PHASE.md) tick checklist, sang Phase 1.
