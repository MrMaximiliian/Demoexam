"""Хеширование и проверка паролей.

Пароли не хранятся в открытом виде. Для каждой учётной записи в базе
хранится SHA-256 хеш строки, включающей соль приложения и логин
пользователя, что исключает совпадение хешей у одинаковых паролей
разных пользователей.
"""

import hashlib

from app import config


class PasswordHasher:
    def __init__(self, salt=config.PASSWORD_SALT):
        self.salt = salt

    def hash(self, login, password):
        raw = "{0}::{1}::{2}".format(self.salt, login.lower(), password)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify(self, login, password, stored_hash):
        return self.hash(login, password) == stored_hash
