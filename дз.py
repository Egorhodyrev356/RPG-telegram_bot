import random
import string
from string import digits

# Запрашиваем параметры у пользователя
length = int(input("Введите длину пароля (от 6 до 20): "))
digits = input("Нужны ли цифры? (да/нет): ").lower() == "да"
specials = input("Нужны ли спецсимволы? (да/нет): ").lower() == "да"

# Базовый набор символов — буквы в обоих регистрах
characters = string.ascii_letters

# Если нужны числа — добавим к базовым допустимым значениям числовые знаки
if digits:
    characters += string.digits

# Если требуются спецсимволы – добавим их тоже!
if specials:
    characters += "!@#$%&*"

password_list=[]
for x in range(length):
     password_list.append(random.choice(characters))

password="".join(password_list)

print(f"Сгенерированный пароль: {password}")