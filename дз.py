import random
import string


# Запрашиваем параметры у пользователя
length = int(input("Введите длину пароля (от 6 до 20): "))
digits = input("Нужны ли цифры? (да/нет): ").lower() == "да"
specials = input("Нужны ли спецсимволы? (да/нет): ").lower() == "да"

# Базовый набор символов — буквы в обоих регистрах
characters = string.ascii_letters

