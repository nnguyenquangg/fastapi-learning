"""
Exercise 05 — Errors & Debugging

Try/except, raise, cách đọc traceback.
"""

# --- Bài 1: Đọc traceback ---
# Chạy code dưới đây, đọc lỗi, trả lời:
# 1. Lỗi tên gì?
# 2. Xảy ra ở dòng nào?
# 3. Tại sao lỗi?

# def broken():
#     x = [1, 2, 3]
#     return x[10]
# broken()

# Viết câu trả lời dưới dạng comment:
# 1. Lỗi tên: IndexError
# 2. Lỗi ở dòng return[10]
# 3. Lỗi vì x chỉ 3 phần tử, index ở trên là 0,1,2. Nhưng code truy cập vào x[10], vị trí này ko tồn tại


# --- Bài 2: Try/except cơ bản ---
# Viết function safe_divide(a, b):
# - Nếu b == 0, bắt ZeroDivisionError và trả về None
# - Nếu a hoặc b không phải số, bắt TypeError và trả về None
# - Thành công → trả về a/b
# Test: safe_divide(10, 2), safe_divide(10, 0), safe_divide("a", 2)
# TODO:
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
    except TypeError:
        return None
#Test
print(safe_divide(10, 2))
print(safe_divide(10, 0))
print(safe_divide("a", 2))


# --- Bài 3: Multiple except ---
# Viết function parse_age(s):
# - Input: str
# - Output: int (tuổi)
# - Xử lý:
#   - ValueError (không phải số) → raise ValueError("Tuổi phải là số")
#   - Nếu < 0 hoặc > 150 → raise ValueError("Tuổi không hợp lệ")
# Test: parse_age("25"), parse_age("abc"), parse_age("-5")
# TODO:
# def parse_age(s):
#     try:
#         age = int(s)
#         if age < 0 or age > 150:
#             raise ValueError("Tuổi không hợp lệ")
#         return age
#     except ValueError:
#         raise ValueError("Tuổi phải là số")
# # Test
# print(parse_age("25"))
# print(parse_age("abc"))
# print(parse_age("-5"))


# --- Bài 4: Finally ---
# Viết function mở file, đọc nội dung, đóng file
# - Dùng try/finally để đảm bảo file luôn đóng
# - Sau đó viết lại version dùng `with open(...)` — so sánh
# TODO:
# Dùng try/finally
# def read_file_1(fileName):
#     f = open(fileName, "r", encoding="utf-8")
#     try:
#         return f.read()
#     finally:
#         f.close()
#         print("Đã đóng file try/finally")

# print(read_file_1("text.txt"))

# # Dùng with open(...)
# def read_file_2(fileName):
#     with open(fileName, "r", encoding="utf-8") as f:
#         content = f.read()
#         print("Đã đóng file with")
#         return content

# try/finally phải tự gọi f.close(), còn with tự đóng file khi thoát khối, kể cả khi có lỗi. Vì vậy with gọn và an toàn hơn


# --- Bài 5: Custom exception ---
# Tạo class InsufficientFundsError(Exception)
# Viết function withdraw(balance, amount):
# - Nếu amount > balance → raise InsufficientFundsError
# - Ngược lại → trả về balance - amount
# Catch và in message thân thiện
# TODO:
class InsufficientFundsError(Exception):
    """Số tiền vượt quá số dư"""
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(
            f"Số dư không đủ: bạn có {balance}, bạn muốn rút {amount}"
        )
    return balance - amount


# --- Bài 6: Debugging với print ---
# Code dưới đây có bug — tìm và fix:
# def average(numbers):
#     total = 0
#     for n in numbers:
#         total + n  # bug ở đây?
#     return total / len(numbers)

# print(average([10, 20, 30]))   # Kỳ vọng 20.0

# Dùng print để debug từng bước, tìm bug
# TODO: fix
def average(numbers):
    total = 0
    for n in numbers:
        total += n  #Thay + thành += hoặc có thể thay total = total + n 
        print('total', total)
    return total / len(numbers)

print(average([10, 20, 30]))

# --- Bài 7: Debugging với pdb (bonus) ---
# Thêm `import pdb; pdb.set_trace()` vào function trên
# Chạy lại, dùng lệnh:
#   n (next), s (step), p <var> (print), c (continue), q (quit)
# Không cần viết code, chỉ thực hành
# import pdb
# def average(numbers):
#     total = 0
#     for n in numbers:
#         pdb.set_trace()
#         total += n
#     return total / len(numbers)

# print(average([10, 20, 30]))


# --- Bài 8: Validation pattern ---
# Viết function register_user(name, age, email):
# - name: str, không rỗng
# - age: int, 13 <= age <= 120
# - email: str, chứa "@"
# Raise ValueError với message rõ ràng cho mỗi điều kiện
# Nếu OK → trả về dict {name, age, email}
# TODO:
def register_user(name, age, email):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Tên phải là chuỗi và không được để trống")
    if not isinstance(age, int) or not 13 <= age <= 120:
        raise ValueError("Tuổi phải là số từ 13 đến 120")
    if not isinstance(email, str) or "@" not in email:
        raise ValueError("Email phải là chuỗi và chứa ký tự @")
    return {
        "name": name,
        "age": age,
        "email": email
    }

print(register_user("Phuc", 25, "phuc@gmail.com"))
print(register_user("", 25, "phuc@gmail.com"))
print(register_user("Phuc", 10, "phuc@gmail.com"))
print(register_user("Phuc", 25, "phucgmail.com"))