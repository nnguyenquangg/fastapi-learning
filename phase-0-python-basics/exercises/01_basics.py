"""
Exercise 01 — Python Basics

Mục tiêu: làm quen với biến, kiểu, input/output.

Yêu cầu: gõ TAY từng bài tập. KHÔNG copy.
Chạy: python 01_basics.py
"""

# --- Bài 1: Hello World ---
# In ra: Hello, FastAPI!
# TODO: viết code dưới đây

print("Hello, FastApi!")

# --- Bài 2: Biến và kiểu ---
# Khai báo các biến sau và in ra type của từng biến:
# - age = 25
# - height = 1.75
# - name = "An"
# - is_student = True
# Gợi ý: dùng type(...)
# TODO:

age = 25
height = 1.75
name = "An"
is_student = True

print(type(age))
print(type(height))
print(type(name))
print(type(is_student))

# --- Bài 3: Input ---
# Hỏi user "Tên bạn là gì? ", lấy input, in ra "Xin chào <tên>"
# TODO:

name = input("Tên bạn là gì?")

print(f"Xin chào {name}")

# --- Bài 4: Arithmetic ---
# Viết chương trình tính BMI
# - Nhập cân nặng (kg), chiều cao (m)
# - Tính BMI = cân nặng / (chiều cao ^ 2)
# - In ra BMI với 2 chữ số thập phân
# Gợi ý: float(input(...)), f"{bmi:.2f}"
# TODO:

weight = float(input("Cân nặng của bạn là:"))
height = float(input("Chiều cao của bạn là:"))

bmi = weight / (height**2)

print(f"BMI của bạn là:{bmi:.2f}")

# --- Bài 5: String formatting ---
# Có 3 biến: name, age, city
# In ra 3 cách khác nhau:
# 1. Dùng + (concat)
# 2. Dùng .format()
# 3. Dùng f-string
# Output: "Tôi là An, 25 tuổi, sống ở Hà Nội."
# TODO:

name = "An"
age = 25
city = "Hà Nội"

print("Tôi là " + name + ", " + str(age) + " tuổi, sống ở " + city + ".")

print("Tôi là {}, {} tuổi, sống ở {}.".format(name, age, city))

print(f"Tôi là {name}, {age} tuổi, sống ở {city}.")

# --- Bài 6: Điều kiện ---
# Phân loại BMI:
# - < 18.5: Gầy
# - 18.5 - 24.9: Bình thường
# - 25 - 29.9: Thừa cân
# - >= 30: Béo phì
# Lấy BMI từ bài 4, in ra phân loại
# TODO:

weight = float(input("Cân nặng của bạn là:"))
height = float(input("Chiều cao của bạn là:"))

bmi = weight / (height**2)

if bmi < 18.5:
    print("Gầy")
elif bmi < 25:
    print("Bình thường")
elif bmi < 30:
    print("Thừa cân")
else:
    print("Béo phì")

# --- Bài 7: Bonus ---
# Viết chương trình đoán số:
# - Máy nghĩ số bí mật (dùng random.randint(1, 100))
# - Cho người dùng đoán, gợi ý "lớn hơn" / "nhỏ hơn"
# - In ra số lần đoán khi đúng
# Gợi ý: import random, while True, break
# TODO:

import random

number = random.randint(1, 100)
number_of_guess = 0

while True:
    guess = int(input("Nhập số bạn đoán:"))
    number_of_guess += 1

    if guess == number:
        print(f"Bạn đã đoán đúng sau {number_of_guess} lần đoán")
        break
    elif guess < number:
        print("Lớn hơn")
    else:
        print("Nhỏ hơn")
