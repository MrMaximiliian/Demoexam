"""Сборка базы данных ИС производства ООО "Хлебус".

Скрипт создаёт файл базы данных SQLite, выполняет DDL-скрипты, импортирует
контрагентов из файла "Заказчики.json" и заполняет демонстрационные заказы
и учётные записи пользователей.

Запуск:  python build_database.py
Результат:  hlebus.db в текущем каталоге.
"""

import hashlib
import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hlebus.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "create_database.sql")
SEED_FILE = os.path.join(BASE_DIR, "seed_reference.sql")
CUSTOMERS_FILE = os.path.join(BASE_DIR, "Заказчики.json")

PASSWORD_SALT = "hlebus"


def hash_password(login, password):
    raw = "{0}::{1}::{2}".format(PASSWORD_SALT, login.lower(), password)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def run_script(connection, path):
    with open(path, encoding="utf-8") as script:
        connection.executescript(script.read())


def import_counterparties(connection):
    with open(CUSTOMERS_FILE, encoding="utf-8") as source:
        records = json.load(source)
    rows = [
        (
            item.get("id"),
            item.get("name"),
            item.get("inn") or None,
            item.get("addres") or None,
            item.get("phone") or None,
            1 if item.get("salesman") else 0,
            1 if item.get("buyer") else 0,
        )
        for item in records
    ]
    connection.executemany(
        """INSERT INTO counterparties
               (code, name, inn, address, phone, is_supplier, is_buyer)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    return len(rows)


def counterparty_id(connection, name):
    cursor = connection.execute(
        "SELECT id FROM counterparties WHERE name = ?", (name,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def add_extra_counterparties(connection):
    extra = [
        ("ООО \"Фрегат\"", "7707083893", "г. Москва, ул. Тверская, 12", "+74951234567", 0, 1),
        ("ООО Молочный комбинат \"Полесье\"", "7710140679", "г. Минск, ул. Промышленная, 8", "+375171002030", 1, 0),
    ]
    connection.executemany(
        """INSERT INTO counterparties
               (name, inn, address, phone, is_supplier, is_buyer)
           VALUES (?, ?, ?, ?, ?, ?)""",
        extra,
    )


def product_id(connection, name):
    cursor = connection.execute("SELECT id FROM products WHERE name = ?", (name,))
    return cursor.fetchone()[0]


def seed_orders(connection):
    orders = [
        {
            "number": "1",
            "date": "2025-06-09",
            "buyer": "ООО \"Ромашка\"",
            "executor": "ООО \"Поставка\"",
            "items": [
                ("Булочка с изюмом", 100, 35),
                ("Хлеб белый 1 кг.", 8, 42),
            ],
        },
        {
            "number": "2",
            "date": "2025-06-10",
            "buyer": "ООО \"Ассоль\"",
            "executor": "ООО \"Ипподром\"",
            "items": [
                ("Булочка с изюмом", 250, 35),
                ("Булочка с корицей", 40, 35),
            ],
        },
        {
            "number": "3",
            "date": "2025-06-07",
            "buyer": "ООО \"Фрегат\"",
            "executor": "ООО Молочный комбинат \"Полесье\"",
            "items": [
                ("Хлеб белый 1 кг.", 8, 45),
                ("Хлеб ржаной 800г.", 7, 47),
            ],
        },
    ]
    for order in orders:
        cursor = connection.execute(
            "INSERT INTO orders (number, order_date, buyer_id, executor_id) VALUES (?, ?, ?, ?)",
            (
                order["number"],
                order["date"],
                counterparty_id(connection, order["buyer"]),
                counterparty_id(connection, order["executor"]),
            ),
        )
        order_id = cursor.lastrowid
        for name, quantity, price in order["items"]:
            connection.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, product_id(connection, name), quantity, price),
            )


def seed_users(connection):
    administrator = connection.execute(
        "SELECT id FROM roles WHERE name = 'Администратор'"
    ).fetchone()[0]
    operator = connection.execute(
        "SELECT id FROM roles WHERE name = 'Пользователь'"
    ).fetchone()[0]
    users = [
        ("admin", "admin123", "Иванов Иван Иванович", administrator),
        ("user", "user123", "Петров Пётр Петрович", operator),
        ("kassir", "kassir2025", "Сидорова Анна Олеговна", operator),
    ]
    connection.executemany(
        """INSERT INTO users (login, password_hash, full_name, role_id)
           VALUES (?, ?, ?, ?)""",
        [
            (login, hash_password(login, password), full_name, role_id)
            for login, password, full_name, role_id in users
        ],
    )


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        run_script(connection, SCHEMA_FILE)
        run_script(connection, SEED_FILE)
        imported = import_counterparties(connection)
        add_extra_counterparties(connection)
        seed_orders(connection)
        seed_users(connection)
        connection.commit()
    finally:
        connection.close()

    print("База данных создана:", DB_PATH)
    print("Импортировано контрагентов из JSON:", imported)


if __name__ == "__main__":
    main()
