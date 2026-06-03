"""Сущность «Роль пользователя»."""


class Role:
    def __init__(self, role_id, name):
        self.id = role_id
        self.name = name

    def __str__(self):
        return self.name
