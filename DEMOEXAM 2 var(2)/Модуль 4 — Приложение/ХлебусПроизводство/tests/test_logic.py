"""Модульные тесты бизнес-логики приложения.

Тесты не требуют графического интерфейса и проверяют ключевые сценарии:
хеширование паролей, аутентификацию, блокировку учётной записи и сборку
пазла-капчи. Запуск:  python -m unittest discover -s tests
"""

import os
import random
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import config
from app.database.connection import DatabaseConnection
from app.database.user_repository import UserRepository
from app.services import (
    AuthenticationService,
    AuthStatus,
    PasswordHasher,
    PuzzleCaptcha,
)

SCHEMA = """
CREATE TABLE roles (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role_id INTEGER NOT NULL REFERENCES roles (id),
    is_blocked INTEGER NOT NULL DEFAULT 0,
    failed_attempts INTEGER NOT NULL DEFAULT 0
);
"""


class LogicTestCase(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.hasher = PasswordHasher()
        raw = sqlite3.connect(self.db_path)
        raw.executescript(SCHEMA)
        raw.execute("INSERT INTO roles (id, name) VALUES (1, 'Администратор'), (2, 'Пользователь')")
        raw.execute(
            "INSERT INTO users (login, password_hash, full_name, role_id) VALUES (?, ?, ?, ?)",
            ("admin", self.hasher.hash("admin", "admin123"), "Администратор", 1),
        )
        raw.commit()
        raw.close()
        self.connection = DatabaseConnection(self.db_path)
        self.repository = UserRepository(self.connection)
        self.auth = AuthenticationService(self.repository, self.hasher)

    def tearDown(self):
        os.remove(self.db_path)

    def test_password_hash_is_not_plaintext(self):
        stored = self.hasher.hash("admin", "admin123")
        self.assertNotEqual(stored, "admin123")
        self.assertTrue(self.hasher.verify("admin", "admin123", stored))
        self.assertFalse(self.hasher.verify("admin", "wrong", stored))

    def test_successful_login(self):
        result = self.auth.authenticate("admin", "admin123", captcha_passed=True)
        self.assertEqual(result.status, AuthStatus.SUCCESS)
        self.assertEqual(result.user.login, "admin")

    def test_empty_fields(self):
        result = self.auth.authenticate("", "", captcha_passed=True)
        self.assertEqual(result.status, AuthStatus.EMPTY_FIELDS)

    def test_unknown_login(self):
        result = self.auth.authenticate("ghost", "123", captcha_passed=True)
        self.assertEqual(result.status, AuthStatus.WRONG_CREDENTIALS)

    def test_wrong_password_increments_attempts(self):
        self.auth.authenticate("admin", "bad", captcha_passed=True)
        user = self.repository.find_by_login("admin")
        self.assertEqual(user.failed_attempts, 1)
        self.assertFalse(user.is_blocked)

    def test_block_after_three_failures(self):
        for _ in range(3):
            result = self.auth.authenticate("admin", "bad", captcha_passed=True)
        self.assertEqual(result.status, AuthStatus.BLOCKED)
        user = self.repository.find_by_login("admin")
        self.assertTrue(user.is_blocked)

    def test_blocked_user_cannot_login_with_correct_password(self):
        for _ in range(3):
            self.auth.authenticate("admin", "bad", captcha_passed=True)
        result = self.auth.authenticate("admin", "admin123", captcha_passed=True)
        self.assertEqual(result.status, AuthStatus.BLOCKED)

    def test_failed_captcha_counts_as_attempt(self):
        result = self.auth.authenticate("admin", "admin123", captcha_passed=False)
        self.assertEqual(result.status, AuthStatus.CAPTCHA_FAILED)
        user = self.repository.find_by_login("admin")
        self.assertEqual(user.failed_attempts, 1)

    def test_successful_login_resets_attempts(self):
        self.auth.authenticate("admin", "bad", captcha_passed=True)
        self.auth.authenticate("admin", "admin123", captcha_passed=True)
        user = self.repository.find_by_login("admin")
        self.assertEqual(user.failed_attempts, 0)

    def test_unblock_resets_state(self):
        for _ in range(3):
            self.auth.authenticate("admin", "bad", captcha_passed=True)
        user = self.repository.find_by_login("admin")
        self.repository.unblock(user.id)
        refreshed = self.repository.find_by_login("admin")
        self.assertFalse(refreshed.is_blocked)
        self.assertEqual(refreshed.failed_attempts, 0)

    def test_duplicate_login_detection(self):
        self.assertTrue(self.repository.login_exists("admin"))
        self.assertFalse(self.repository.login_exists("newbie"))

    def test_create_user(self):
        self.repository.create_user(
            "newbie", self.hasher.hash("newbie", "pass"), "Новый", 2
        )
        self.assertTrue(self.repository.login_exists("newbie"))


class CaptchaTestCase(unittest.TestCase):
    def test_shuffle_is_not_solved(self):
        puzzle = PuzzleCaptcha(config.CAPTCHA_GRID_SIZE, rng=random.Random(7))
        puzzle.shuffle()
        self.assertFalse(puzzle.is_solved())

    def test_swap_restores_solution(self):
        puzzle = PuzzleCaptcha(2)
        puzzle.arrangement = [1, 0, 2, 3]
        self.assertFalse(puzzle.is_solved())
        puzzle.swap(0, 1)
        self.assertTrue(puzzle.is_solved())


if __name__ == "__main__":
    unittest.main()
