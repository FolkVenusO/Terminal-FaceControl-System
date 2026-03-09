import sqlite3
import datetime
import os
import time
from colorama import init, Fore, Style
from prettytable import PrettyTable

init(autoreset=True)

connection = sqlite3.connect('guests.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        height REAL,
        visit_time TEXT
    )
''')

def can_guest_enter(age, height):
    return age >= 16 or (age >= 12 and height >= 160)

def ask_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print(Fore.RED + "Ошибка! Введите целое число.")

def ask_float(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print(Fore.RED + "Ошибка! Введите число.")

passed_guests = []

cursor.execute('SELECT name, age, height, visit_time FROM guests')
rows = cursor.fetchall()

for row in rows:
    guest_card = {
        "имя": row[0],
        "возраст": row[1],
        "рост": row[2],
        "время": row[3]
    }
    passed_guests.append(guest_card)

rejected = 0

while True:
    os.system('cls')
    age = ask_int(Fore.WHITE + "Возраст (0 для выхода): ")

    if age < 0:
        print(Fore.RED + "Возраст не может быть отрицательным.")
        time.sleep(2) 
        continue

    if age == 0:
        print(Fore.CYAN +"Завершение работы...")
        break

    height = ask_float(Fore.WHITE + "Рост: ")

    if height < 0:
        print(Fore.RED + "Рост не может быть отрицательным.")
        time.sleep(2) 
        continue

    print(Fore.YELLOW + "⏳ Проверка по базе данных...")
    time.sleep(1.5) 

    if can_guest_enter(age, height):
        print(Fore.GREEN + "Проходите!")
        time.sleep(1) 
        name = input(Fore.WHITE + "Как вас зовут? ").strip()

        now = datetime.datetime.now().strftime("%H:%M:%S") 

        if not name:
            print(Fore.RED + "Имя не может быть пустым.")
            time.sleep(2) 
            continue

        guest_card = {
            "имя": name,
            "возраст": age,
            "рост": height,
            "время": now
        }
        passed_guests.append(guest_card)

        cursor.execute(
            'INSERT INTO guests (name, age, height, visit_time) VALUES (?, ?, ?, ?)',
            (name, age, height, now)
        )
        connection.commit()
        print(Fore.GREEN + "Гость успешно записан!")
        time.sleep(2)
    else:
        print(Fore.RED + "Извини, ты не подходишь по критериям.")
        time.sleep(2)
        rejected += 1

print(Fore.CYAN + "\n--- ИТОГОВЫЙ ОТЧЕТ ---")
print(Fore.WHITE + "Все прошедшие гости:")

table = PrettyTable()

table.field_names = ["Имя", "Возраст", "Рост", "Время визита"]

for guest in passed_guests:
    table.add_row([guest["имя"], guest["возраст"], guest["рост"], guest["время"]])

print(Fore.CYAN + str(table))

print(Fore.RED + f"\nОтклоненные: {rejected}")

if passed_guests:
    total_age = sum(guest["возраст"] for guest in passed_guests)
    average_age = total_age / len(passed_guests)
    print(f"Средний возраст посетителей: {average_age:.1f}")

    oldest_guest = max(passed_guests, key=lambda guest: guest["возраст"])
    print(f'Самый старший посетитель: {oldest_guest["имя"]} ({oldest_guest["возраст"]})')

print(f"Всего прошли {len(passed_guests)} человек.")

connection.close()
