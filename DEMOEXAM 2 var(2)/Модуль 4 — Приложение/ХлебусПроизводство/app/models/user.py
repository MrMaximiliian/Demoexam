"""Сущность «Пользователь информационной системы»."""

from app import config


class User:
    def __init__(self, user_id, login, full_name, role_id, role_name,
                 is_blocked=False, failed_attempts=0, password_hash=None):
        self.id = user_id
        self.login = login
        self.full_name = full_name
        self.role_id = role_id
        self.role_name = role_name
        self.is_blocked = bool(is_blocked)
        self.failed_attempts = failed_attempts
        self.password_hash = password_hash

    @property
    def is_administrator(self):
        return self.role_name == config.ROLE_ADMINISTRATOR

    @property
    def status_text(self):
        return "Заблокирован" if self.is_blocked else "Активен"

    @property
    def display_name(self):
        return self.full_name or self.login
