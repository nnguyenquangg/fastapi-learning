"""
Exercise 02 — Collections & Control Flow

List, dict, set, tuple + for/while.
"""

# --- Bài 1: List basics ---
# Tạo list chứa tên 5 ngôn ngữ lập trình
# - In độ dài
# - In phần tử đầu và cuối
# - Thêm "Python" vào cuối
# - Xoá phần tử thứ 2
# - Sắp xếp theo alphabet
# TODO:


# --- Bài 2: List comprehension ---
# Cho list numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# Dùng list comprehension để tạo:
# 1. List bình phương: [1, 4, 9, ...]
# 2. List số chẵn: [2, 4, 6, 8, 10]
# 3. List chuỗi "Số N là chẵn/lẻ"
# TODO:


# --- Bài 3: Dict ---
# Tạo dict user = {"name": "An", "age": 25, "email": "an@example.com"}
# - Truy cập name
# - Thêm key "city" = "HN"
# - Xoá key "age"
# - In toàn bộ key-value bằng for loop
# - Kiểm tra "email" có trong dict không
# TODO:


# --- Bài 4: Nested data ---
# Có danh sách students:
students = [
    {"name": "An", "scores": [8, 7, 9]},
    {"name": "Bình", "scores": [6, 7, 8]},
    {"name": "Châu", "scores": [9, 10, 9]},
]
# Yêu cầu:
# 1. In tên + điểm trung bình của từng học sinh
# 2. Tìm học sinh có điểm trung bình cao nhất
# 3. In danh sách học sinh có điểm TB >= 8
# TODO:


# --- Bài 5: Set ---
# Có 2 danh sách môn học
math_students = ["An", "Bình", "Châu", "Dũng"]
physics_students = ["Bình", "Châu", "Em", "Phương"]
# Dùng set:
# 1. Tìm học sinh học CẢ 2 môn
# 2. Tìm học sinh chỉ học Toán (không học Lý)
# 3. Tìm toàn bộ học sinh (union)
# TODO:


# --- Bài 6: Loop pattern ---
# Đếm số ký tự xuất hiện trong chuỗi:
text = "hello world"
# Output: {"h": 1, "e": 1, "l": 3, "o": 2, " ": 1, "w": 1, "r": 1, "d": 1}
# TODO:


# --- Bài 7: FizzBuzz ---
# In số từ 1 đến 30
# - Chia hết 3 → "Fizz"
# - Chia hết 5 → "Buzz"
# - Chia hết cả 3 và 5 → "FizzBuzz"
# - Còn lại → số
# TODO:
