"""
Exercise 01 — Python Basics

Mục tiêu: làm quen với biến, kiểu, input/output.

Yêu cầu: gõ TAY từng bài tập. KHÔNG copy.
Chạy: python 01_basics.py
"""

# --- Bài 1: Hello World ---
# In ra: Hello, FastAPI!
# TODO: viết code dưới đây

#In ra
print("Hello, FastAPI!")

# --- Bài 2: Biến và kiểu ---
# Khai báo các biến sau và in ra type của từng biến:
# - age = 25
# - height = 1.75
# - name = "An"
# - is_student = True
# Gợi ý: dùng type(...)
# TODO:

#Khai báo biến
age = 25
height = 1.75
name = "An"
is_student = True
#In ra tyoe
print(type(age))
print(type(height))
print(type(name))
print(type(is_student))

# --- Bài 3: Input ---
# Hỏi user "Tên bạn là gì? ", lấy input, in ra "Xin chào <tên>"
# TODO:

#Hỏi tên user
name = input("Tên của bạn là gì? ")
#In lời chào
print(f"Xin chào {name}")


# --- Bài 4: Arithmetic ---
# Viết chương trình tính BMI
# - Nhập cân nặng (kg), chiều cao (m)
# - Tính BMI = cân nặng / (chiều cao ^ 2)
# - In ra BMI với 2 chữ số thập phân
# Gợi ý: float(input(...)), f"{bmi:.2f}"
# TODO:

#Nhập cân nặng, chiều cao
weight = float(input("Nhập cân nặng (kg): "))
height = float(input("Nhập chiều cao (m): "))
#Tính BMI
bmi = weight / (height ** 2)
#In ra BMI với 2 chữ số thập phân
print(f"BMI của bạn là: {bmi: 2f}")

# --- Bài 5: String formatting ---
# Có 3 biến: name, age, city
# In ra 3 cách khác nhau:
# 1. Dùng + (concat)
# 2. Dùng .format()
# 3. Dùng f-string
# Output: "Tôi là An, 25 tuổi, sống ở Hà Nội."
# TODO:

#Khai báo biến
name = "An"
age = 25
city = "Hà Nội"
#In bằng concat
print("Tôi là " + name + ", " + str(age) + " tuổi, sống ở " + city + ".")
#In bằng format
print("Tôi là {}, {} tuổi, sống ở {}.".format(name, age, city))
#In bằng f-string
print(f"Tôi là {name}, {age} tuổi, sống ở {city}")

# --- Bài 6: Điều kiện ---
# Phân loại BMI:
# - < 18.5: Gầy
# - 18.5 - 24.9: Bình thường
# - 25 - 29.9: Thừa cân
# - >= 30: Béo phì
# Lấy BMI từ bài 4, in ra phân loại
# TODO:

#Phân loại BMI
if bmi < 18.5:
  print("Phân loại: Gầy")
elif bmi < 25:
  print("Phân loại: Bình thường")
elif bmi < 25:
  print("Phân loại: Thừa cân")
elif:
  print("Phân loại: Béo phì")


# --- Bài 7: Bonus ---
# Viết chương trình đoán số:
# - Máy nghĩ số bí mật (dùng random.randint(1, 100))
# - Cho người dùng đoán, gợi ý "lớn hơn" / "nhỏ hơn"
# - In ra số lần đoán khi đúng
# Gợi ý: import random, while True, break
# TODO:

secret_number = random.randint(1, 100)
att = 0

while True:
    guess = int(input("Đoán số từ 1 đến 100: "))
    att += 1

    if guess == secret_number:
      print("Chính xác")
      print(f"Bạn đã đoán dúng sau {att} lần")
      break
    elif guess < secret_number:
      print("Lớn hơn")
    else: 
      print("Nhỏ hơn")
