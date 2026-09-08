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


# Tạo list

languages = ["JavaScript", "Java", "C#", "Go", "Ruby"]

# In độ dài

print(len(languages))

# In phần tử đầu

print(languages[0])

# In phần tử cuối

print(languages[-1])

# Thêm "Python" và cuối

languages.append("Python")

# Xoá phần tử thứ 2

languages.pop(2)

# Sắp xếp theo alphabet

languages.sort()


# --- Bài 2: List comprehension ---

# Cho list numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Dùng list comprehension để tạo:

# 1. List bình phương: [1, 4, 9, ...]

# 2. List số chẵn: [2, 4, 6, 8, 10]

# 3. List chuỗi "Số N là chẵn/lẻ"

# TODO:


# list
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# In list bình phương

squares = [n**2 for n in numbers]

print(squares)

# In list số chẵn

even_nums = [n for n in numbers if n % 2 == 0]

# In list chuỗi "Số N là chẵn/lẻ"

result = [f"Số {n} là {'chẵn' if n % 2 == 0 else 'lẻ'}" for n in numbers]


# --- Bài 3: Dict ---

# Tạo dict user = {"name": "An", "age": 25, "email": "an@example.com"}

# - Truy cập name

# - Thêm key "city" = "HN"

# - Xoá key "age"

# - In toàn bộ key-value bằng for loop

# - Kiểm tra "email" có trong dict không

# TODO:

# Dict user
user = {"name": "An", "age": 25, "email": "an@example.com"}

# Truy cập name

print(user["name"])

# Thêm key

user["city"] = "HN"

# Xoá key

del user["age"]

# In toàn bộ key-value

for key, value in user.items():
    print(key, ":", value)

# Kiểm tra email

if "email" in user:
    print("Email có trong dict")

else:
    print("Email không có trong dict")


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


# In tên + điểm trung bình

for student in students:
    average = sum(student["scores"]) / len(student["scores"])

    print(f"{student['name']} : {average:.2f}")

# Học sinh có điểm trung bình cao nhất

best_student = max(
    students, key=lambda student: sum(student["scores"]) / len(student["scores"])
)


best_average = sum(best_student["scores"]) / len(student["scores"])

print(
    f"Học sinh có diểm trung bình cao nhất: {best_student['name']} - {best_average:.2f}"
)

# Danh sách học sinh có điểm TB >= 8

good_students = [
    student["name"]
    for student in students
    if sum(student["scores"]) / len(student["scores"]) >= 8
]

print(f"Học sinh có điểm TB >= 8:", good_students)


# --- Bài 5: Set ---

# Có 2 danh sách môn học

math_students = ["An", "Bình", "Châu", "Dũng"]

physics_students = ["Bình", "Châu", "Em", "Phương"]

# Dùng set:

# 1. Tìm học sinh học CẢ 2 môn

# 2. Tìm học sinh chỉ học Toán (không học Lý)

# 3. Tìm toàn bộ học sinh (union)

# TODO:


math_set = set(math_students)

physics_set = set(physics_students)

# Học sinh học cả 2 môn

both = math_set & physics_set

print("Học cả 2 môn:", both)

# Chỉ học toán

only_math = math_set - physics_set

print("Học chỉ học toán:", only_math)

# Tất cả học sinh

all_students = math_set | physics_set

print("Toàn bộ học sinh:", all_students)


# --- Bài 6: Loop pattern ---

# Đếm số ký tự xuất hiện trong chuỗi:

text = "hello world"

# Output: {"h": 1, "e": 1, "l": 3, "o": 2, " ": 1, "w": 1, "r": 1, "d": 1}

# TODO:

char_count = {}

for char in text:
    if char in char_count:
        char_count[char] += 1

    else:
        char_count[char] = 1

print(char_count)


# --- Bài 7: FizzBuzz ---

# In số từ 1 đến 30

# - Chia hết 3 → "Fizz"

# - Chia hết 5 → "Buzz"

# - Chia hết cả 3 và 5 → "FizzBuzz"

# - Còn lại → số

# TODO:

for i in range(1, 31):
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")

    elif i % 3 == 0:
        print("Fizz")

    elif i % 5 == 0:
        print("Buzz")

    else:
        print(i)
