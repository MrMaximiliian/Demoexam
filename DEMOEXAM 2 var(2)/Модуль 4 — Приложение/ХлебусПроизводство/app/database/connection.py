"""Подключение к базе данных SQLite.

Класс инкапсулирует создание соединения, включение контроля ссылочной
целостности и выдачу строк в виде sqlite3.Row для доступа по именам столбцов.
"""

import os
import sqlite3


class DatabaseError(Exception):
    """Ошибка работы с базой данных, понятная пользовательскому слою."""


class DatabaseConnection:
    def __init__(self, database_path):
        self.database_path = database_path

    def connect(self):
        if not os.path.exists(self.database_path):
            raise DatabaseError(
                "Файл базы данных не найден: {0}".format(self.database_path)
            )
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def query(self, sql, parameters=()):
        connection = self.connect()
        try:
            cursor = connection.execute(sql, parameters)
            return cursor.fetchall()
        finally:
            connection.close()

    def execute(self, sql, parameters=()):
        connection = self.connect()
        try:
            cursor = connection.execute(sql, parameters)
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()
