"""
Exercise 03 — Functions

Viết function, parameter, return, scope.
"""

# --- Bài 1: Basic function ---
# Viết function greet(name) trả về chuỗi "Xin chào, <name>!"
# TODO:
def greet(name):
    return f"Xin chào, {name}"
print(greet("Phuc"))


# --- Bài 2: Default argument ---
# Viết function calculate_price(price, discount=0, tax=0.1)
# Trả về: price * (1 - discount) * (1 + tax)
# Test với: calculate_price(100), calculate_price(100, 0.2), calculate_price(100, 0.1, 0.08)
# TODO:
def calculate_price(price, discount=0, tax=0.1):
    return price * (1 - discount) * (1 + tax)

print (calculate_price(100))
print (calculate_price(100, 0.2))
print (calculate_price(100, 0.1, 0.08))


# --- Bài 3: Multiple return ---
# Viết function divide(a, b) trả về (quotient, remainder)
# Nếu b == 0, return (None, None)
# TODO:
def divide(a, b):
    if b == 0:
        return None, None

    quotient = a // b
    remainder = a % b

    return quotient, remainder
    
print(divide(10, 3))


# --- Bài 4: *args ---
# Viết function sum_all(*numbers) nhận không giới hạn số, trả về tổng
# Test: sum_all(1, 2, 3), sum_all(1, 2, 3, 4, 5)
# TODO:
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3))
print(sum_all(1, 2, 3, 4, 5))


# --- Bài 5: **kwargs ---
# Viết function create_user(**info) in ra tất cả thông tin nhận được
# Test: create_user(name="An", age=25, email="an@x.com")
# TODO:
def create_user(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

create_user(name="An", age=25, email="an@x.com")

# --- Bài 6: Higher-order function ---
# Viết function apply_to_list(lst, func) áp dụng func lên mỗi phần tử
# Test với lambda: apply_to_list([1,2,3], lambda x: x*2) → [2,4,6]
# TODO:
def  apply_to_list(lst, func):
    result = []
    for item in lst:
        result.append(func(item))
    return result

numbers = apply_to_list([1, 2, 3], lambda x: x * 2)
print(numbers)


# --- Bài 7: Recursion ---
# Viết function factorial(n) tính n! bằng đệ quy
# 5! = 5*4*3*2*1 = 120
# TODO:
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))


# --- Bài 8: Scope ---
# Đoán output TRƯỚC khi chạy:
x = 10
def modify():
    x = 20
    print("inside:", x)
modify()
print("outside:", x)
# Viết comment giải thích tại sao

# Sau đó, sửa function để thay đổi được biến x ở scope ngoài
# Gợi ý: global hoặc return
# TODO:

# x = 10 nằm ở bên ngoài function => x này thuộc global scope
# Tạo biến x mới trong function x = 20 => x này thuộc local scope
# Khi đó x trong function sẽ được lấy giá trị là 20
# Gọi function modify() => x bên trong được tạo và sử dụng => inside: 20
# Sau khi function chạy x bên ngoài vẫn là 10 => Vì x = 20 chỉ tồn tại bên trong function => outside: 10

# Sửa function để thay đổi được x ở scope ngoài
x = 10
def modify():
    global x
    x = 20
    print("inside:", x)
modify()
print("outside:", x)


# --- Bài 9: Pure function ---
# Viết 2 function:
# 1. append_item_bad(lst, item) → thêm vào list gốc (có side effect)
# 2. append_item_good(lst, item) → trả về list mới, không thay đổi list gốc
# So sánh output khi gọi 2 lần với cùng input
# TODO:

def append_item_bad(lst, item):
    lst.append(item)
    return lst

def append_item_good(lst, item):
    new_list = lst.copy()
    new_list.append(item)
    return new_list

#Test function append_item_bad
numbers = [1,2,3]
print("List ban đầu:", numbers)
result_bad = append_item_bad(numbers, 4)
print("Kết quả bad:", result_bad)
print("List gốc sau bad:", numbers)

#Test function append_item_good
numbers = [1,2,3]
print("List ban đầu:", numbers)
result_good = append_item_good(numbers, 4)
print("Kết quả good:", result_bad)
print("List gốc sau good:", numbers)


# --- Bài 10: Docstring ---
# Viết function is_prime(n) kiểm tra n có phải số nguyên tố
# Thêm docstring đầy đủ (mô tả, args, returns, example)
# TODO:

def is_prime(n):
    #Kiểm tra một số có phải số nguyên tố ko
    #Args: n(int): Số nguyên tố cần kiểm tra
    #returns: bool: true nếu n là số nguyên tố, false nếu ko phải
    #example:
    #is_prime(7) => true
    #is_prime(10) => false
    #is_prime(1) => false

    if n < 2:
        return False
    
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
        
    return True
print(is_prime(7))
print(is_prime(10))
print(is_prime(1))
print(is_prime(2))