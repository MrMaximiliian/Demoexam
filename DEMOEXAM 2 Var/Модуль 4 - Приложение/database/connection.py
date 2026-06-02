# -*- coding: utf-8 -*-
# Подключение к базе данных "Хлебокомбинат" (MS SQL Server)

import pyodbc

# Параметры подключения. Указать имя своего сервера.
SERVER = r"localhost\SQLEXPRESS"
DATABASE = "Хлебокомбинат"

# Доверенное соединение Windows. Для входа по логину SQL Server заменить
# Trusted_Connection на UID=...;PWD=...
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)
