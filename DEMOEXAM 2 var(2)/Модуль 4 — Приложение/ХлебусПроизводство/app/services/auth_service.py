"""Сервис аутентификации пользователей.

Реализует проверку учётных данных, контроль прохождения капчи и блокировку
учётной записи после трёх неудачных попыток подряд (неверный пароль или
неверно собранный пазл).
"""

import enum

from app import config


class AuthStatus(enum.Enum):
    SUCCESS = "success"
    EMPTY_FIELDS = "empty_fields"
    WRONG_CREDENTIALS = "wrong_credentials"
    CAPTCHA_FAILED = "captcha_failed"
    BLOCKED = "blocked"


class AuthResult:
    def __init__(self, status, user=None):
        self.status = status
        self.user = user

    @property
    def is_success(self):
        return self.status == AuthStatus.SUCCESS


class AuthenticationService:
    def __init__(self, user_repository, password_hasher,
                 max_attempts=config.MAX_FAILED_ATTEMPTS):
        self.users = user_repository
        self.hasher = password_hasher
        self.max_attempts = max_attempts

    def authenticate(self, login, password, captcha_passed):
        login = (login or "").strip()
        if not login or not password:
            return AuthResult(AuthStatus.EMPTY_FIELDS)

        user = self.users.find_by_login(login)
        if user is None:
            return AuthResult(AuthStatus.WRONG_CREDENTIALS)

        if user.is_blocked:
            return AuthResult(AuthStatus.BLOCKED)

        if not captcha_passed:
            return self._register_failure(user, AuthStatus.CAPTCHA_FAILED)

        if not self.hasher.verify(login, password, user.password_hash):
            return self._register_failure(user, AuthStatus.WRONG_CREDENTIALS)

        self.users.reset_failed_attempts(user.id)
        return AuthResult(AuthStatus.SUCCESS, user)

    def _register_failure(self, user, reason):
        self.users.increment_failed_attempts(user.id)
        attempts = user.failed_attempts + 1
        if attempts >= self.max_attempts:
            self.users.set_blocked(user.id, True)
            return AuthResult(AuthStatus.BLOCKED)
        return AuthResult(reason)
