# -*- coding: utf-8 -*-
# Доступ к данным таблицы "Пользователи"

from config import MAX_LOGIN_ATTEMPTS
from database.connection import get_connection
from models.user import User


class UserRepository:
    def find_by_login(self, login):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_пользователя, логин, пароль, роль, заблокирован, "
                "число_попыток FROM Пользователи WHERE логин = ?", login)
            row = cursor.fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return User(row[0], row[1], row[2], row[3], bool(row[4]), row[5])

    def register_failed_attempt(self, user):
        """Учитывает неудачную попытку входа. При достижении предела
        блокирует учётную запись. Возвращает признак блокировки."""
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE Пользователи SET число_попыток = число_попыток + 1 "
                "WHERE id_пользователя = ?", user.user_id)
            cursor.execute(
                "SELECT число_попыток FROM Пользователи "
                "WHERE id_пользователя = ?", user.user_id)
            attempts = cursor.fetchone()[0]
            blocked = attempts >= MAX_LOGIN_ATTEMPTS
            if blocked:
                cursor.execute(
                    "UPDATE Пользователи SET заблокирован = 1 "
                    "WHERE id_пользователя = ?", user.user_id)
            connection.commit()
        finally:
            connection.close()
        return blocked

    def reset_attempts(self, user):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE Пользователи SET число_попыток = 0 "
                "WHERE id_пользователя = ?", user.user_id)
            connection.commit()
        finally:
            connection.close()

    def get_all(self):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_пользователя, логин, пароль, роль, заблокирован, "
                "число_попыток FROM Пользователи ORDER BY id_пользователя")
            rows = cursor.fetchall()
        finally:
            connection.close()
        return [User(r[0], r[1], r[2], r[3], bool(r[4]), r[5]) for r in rows]

    def exists(self, login):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM Пользователи WHERE логин = ?", login)
            found = cursor.fetchone() is not None
        finally:
            connection.close()
        return found

    def add(self, login, password, role):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Пользователи (логин, пароль, роль) "
                "VALUES (?, ?, ?)", login, password, role)
            connection.commit()
        finally:
            connection.close()

    def update(self, user):
        """Сохраняет изменения пользователя. При снятии блокировки счётчик
        попыток обнуляется."""
        connection = get_connection()
        try:
            cursor = connection.cursor()
            blocked_flag = 1 if user.blocked else 0
            attempts = user.attempts if user.blocked else 0
            cursor.execute(
                "UPDATE Пользователи SET логин = ?, пароль = ?, роль = ?, "
                "заблокирован = ?, число_попыток = ? WHERE id_пользователя = ?",
                user.login, user.password, user.role, blocked_flag,
                attempts, user.user_id)
            connection.commit()
        finally:
            connection.close()
