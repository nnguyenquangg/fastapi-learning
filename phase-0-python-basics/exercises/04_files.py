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
with open("note.txt", "w") as f:
    f.write("Today is...\n")
    f.write("I'm learning Python\n")
    f.write("Next: FastAPI\n")


# --- Bài 2: Đọc file ---
# Đọc lại file "note.txt" và:
# 1. In toàn bộ nội dung
# 2. In số dòng
# 3. In số từ (dùng split())
# TODO:
with open("note.txt","r", encoding='utf-8') as f:
    content = f.read()
print("Nội dung file:")
print(content)

print("Số dòng:", len(content.splitlines()))
print("Số từ:", len(content.split()))


# --- Bài 3: Pathlib ---
# Dùng pathlib.Path để:
# 1. Kiểm tra file "note.txt" tồn tại không
# 2. In absolute path
# 3. In kích thước file (bytes)
# 4. Tạo thư mục "data/"
# 5. Copy nội dung note.txt vào "data/note_copy.txt"
# TODO:
from pathlib import Path
file_path = Path("note.txt")

if file_path.exists():
    print("file tồn tại")
    print("Absolute path:", file_path.absolute)
    print("Kích thước:", file_path.stat().st_size, "bytes")

    data = Path("data")
    data.mkdir(exist_ok=True)

    copy_data = data / "note_copy.txt"
    copy_data.write_text(file_path.read_text(encoding="utf-8")),
    print("Đã copy:", copy_data)
else:
    print("File ko tồn tại")




# --- Bài 4: JSON ---
# Tạo dict:
# user = {
#     "name": "An",
#     "age": 25,
#     "hobbies": ["code", "đọc sách", "chạy bộ"],
# }
# 1. Ghi vào file "user.json" (dùng json.dump, ensure_ascii=False, indent=2)
# 2. Đọc lại, in hobbies
# 3. Thêm hobby mới, ghi đè lại file
# TODO:

import json
user = {
    "name": "An",
    "age": 25,
    "hobbies": ["code", "đọc sách", "chạy bộ"],
}
#Ghi vào file "user.json" 
with open("user.json", "w", encoding="utf-8") as f:
    json.dump(user, f, ensure_ascii=False, indent=2)
#Đọc lại, in hobbies
with open("user.json", "r", encoding="utf-8") as f:
    user = json.load(f)
print(user["hobbies"])
#Thêm hobby mới, ghi đè lại file
user["hobbies"].append("Chơi game")
with open("user.json", "w", encoding="utf-8") as f:
    json.dump(user, f, ensure_ascii=False, indent=2)
print(user["hobbies"])


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
import csv
#Ghi vào file "student.csv"
with open("student.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(students_data)
#Đọc lại và in bảng đẹp
with open("student.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(f"{row[0]:<5} {row[1]:<5} {row[2]:<5}")


# --- Bài 6: Module ---
# Tạo file utils.py cùng thư mục với nội dung:
#   def is_even(n): return n % 2 == 0
#   def is_odd(n): return n % 2 == 1
#
# Ở file này, import utils và dùng 2 function trên
# TODO:
import utils

print(utils.is_even(10))
print(utils.is_odd(7))


# --- Bài 7: Mini — Word counter ---
# Viết chương trình đọc file text bất kỳ và in:
# - Top 10 từ xuất hiện nhiều nhất
# - Đã loại stopwords: ["the", "a", "an", "is", "are", "of", "in", "to"]
# Gợi ý: dùng collections.Counter
# TODO:
from collections import Counter

#Ds từ đã loại
stopwords = ["the", "a", "an", "is", "are", "of", "in", "to"]
#Đọc file
with open("text.txt", "r", encoding="utf-8") as f:
    text = f.read()
text = text.lower()
words = text.split()
file_words = [
    word
    for word in words
    if word not in stopwords
]
counter = Counter(file_words)
top_10 = counter.most_common(10)
print(top_10)
