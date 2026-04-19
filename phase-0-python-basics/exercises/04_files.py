"""
Exercise 04 — Files & Modules

Đọc/ghi file, JSON, pathlib, import.
"""

# --- Bài 1: Ghi file text ---
# Ghi vào file "note.txt" 3 dòng:
# - Dòng 1: "Today is..."
# - Dòng 2: "I'm learning Python"
# - Dòng 3: "Next: FastAPI"
# Dùng with open(...) as f:
# TODO:


# --- Bài 2: Đọc file ---
# Đọc lại file "note.txt" và:
# 1. In toàn bộ nội dung
# 2. In số dòng
# 3. In số từ (dùng split())
# TODO:


# --- Bài 3: Pathlib ---
# Dùng pathlib.Path để:
# 1. Kiểm tra file "note.txt" tồn tại không
# 2. In absolute path
# 3. In kích thước file (bytes)
# 4. Tạo thư mục "data/"
# 5. Copy nội dung note.txt vào "data/note_copy.txt"
# TODO:


# --- Bài 4: JSON ---
# Tạo dict:
user = {
    "name": "An",
    "age": 25,
    "hobbies": ["code", "đọc sách", "chạy bộ"],
}
# 1. Ghi vào file "user.json" (dùng json.dump, ensure_ascii=False, indent=2)
# 2. Đọc lại, in hobbies
# 3. Thêm hobby mới, ghi đè lại file
# TODO:


# --- Bài 5: CSV ---
# Có dữ liệu:
students_data = [
    ["name", "age", "grade"],
    ["An", 18, 9.5],
    ["Bình", 17, 8.0],
    ["Châu", 19, 9.0],
]
# 1. Ghi vào "students.csv" (dùng csv module)
# 2. Đọc lại và in bảng đẹp
# TODO:


# --- Bài 6: Module ---
# Tạo file utils.py cùng thư mục với nội dung:
#   def is_even(n): return n % 2 == 0
#   def is_odd(n): return n % 2 == 1
#
# Ở file này, import utils và dùng 2 function trên
# TODO:


# --- Bài 7: Mini — Word counter ---
# Viết chương trình đọc file text bất kỳ và in:
# - Top 10 từ xuất hiện nhiều nhất
# - Đã loại stopwords: ["the", "a", "an", "is", "are", "of", "in", "to"]
# Gợi ý: dùng collections.Counter
# TODO:
