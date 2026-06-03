"""Репозиторий пользователей и ролей.

Содержит операции чтения и изменения учётных записей. Все обращения к
таблицам users и roles собраны в одном классе, чтобы остальные слои
не зависели от структуры базы данных.
"""

from app.models import Role, User

SELECT_USER = """
    SELECT u.id, u.login, u.full_name, u.role_id, r.name AS role_name,
           u.is_blocked, u.failed_attempts, u.password_hash
    FROM users AS u
    JOIN roles AS r ON r.id = u.role_id
"""


class UserRepository:
    def __init__(self, connection):
        self.connection = connection

    def _build_user(self, row):
        return User(
            user_id=row["id"],
            login=row["login"],
            full_name=row["full_name"],
            role_id=row["role_id"],
            role_name=row["role_name"],
            is_blocked=row["is_blocked"],
            failed_attempts=row["failed_attempts"],
            password_hash=row["password_hash"],
        )

    def find_by_login(self, login):
        rows = self.connection.query(
            SELECT_USER + " WHERE u.login = ?", (login,)
        )
        return self._build_user(rows[0]) if rows else None

    def list_users(self):
        rows = self.connection.query(SELECT_USER + " ORDER BY u.login")
        return [self._build_user(row) for row in rows]

    def list_roles(self):
        rows = self.connection.query("SELECT id, name FROM roles ORDER BY id")
        return [Role(row["id"], row["name"]) for row in rows]

    def login_exists(self, login):
        rows = self.connection.query(
            "SELECT 1 FROM users WHERE login = ?", (login,)
        )
        return len(rows) > 0

    def create_user(self, login, password_hash, full_name, role_id):
        return self.connection.execute(
            """INSERT INTO users (login, password_hash, full_name, role_id)
               VALUES (?, ?, ?, ?)""",
            (login, password_hash, full_name, role_id),
        )

    def update_user(self, user_id, full_name, role_id, is_blocked):
        self.connection.execute(
            """UPDATE users
               SET full_name = ?, role_id = ?, is_blocked = ?
               WHERE id = ?""",
            (full_name, role_id, 1 if is_blocked else 0, user_id),
        )

    def change_password(self, user_id, password_hash):
        self.connection.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
        )

    def increment_failed_attempts(self, user_id):
        self.connection.execute(
            "UPDATE users SET failed_attempts = failed_attempts + 1 WHERE id = ?",
            (user_id,),
        )

    def reset_failed_attempts(self, user_id):
        self.connection.execute(
            "UPDATE users SET failed_attempts = 0 WHERE id = ?",
            (user_id,),
        )

    def set_blocked(self, user_id, is_blocked):
        self.connection.execute(
            "UPDATE users SET is_blocked = ? WHERE id = ?",
            (1 if is_blocked else 0, user_id),
        )

    def unblock(self, user_id):
        self.connection.execute(
            "UPDATE users SET is_blocked = 0, failed_attempts = 0 WHERE id = ?",
            (user_id,),
        )
