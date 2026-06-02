# -*- coding: utf-8 -*-
# Класс сущности "Пользователь"


class User:
    def __init__(self, user_id, login, password, role, blocked, attempts):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.role = role
        self.blocked = blocked
        self.attempts = attempts

    def is_admin(self):
        return self.role == "Администратор"
