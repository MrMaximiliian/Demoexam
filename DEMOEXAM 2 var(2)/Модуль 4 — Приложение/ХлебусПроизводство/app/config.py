"""Параметры приложения и тексты сообщений, общие для всех модулей."""

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(ROOT_DIR, "hlebus.db")
CAPTCHA_IMAGE = os.path.join(os.path.dirname(__file__), "assets", "captcha_source.png")

COMPANY_NAME = "ООО «Хлебус»"
WINDOW_TITLE_PREFIX = "Хлебус"

MAX_FAILED_ATTEMPTS = 3
CAPTCHA_GRID_SIZE = 3
PASSWORD_SALT = "hlebus"

ROLE_ADMINISTRATOR = "Администратор"
ROLE_USER = "Пользователь"

MESSAGE_EMPTY_FIELDS = "Введите логин и пароль — оба поля обязательны для заполнения."
MESSAGE_WRONG_CREDENTIALS = (
    "Вы ввели неверный логин или пароль. "
    "Пожалуйста проверьте ещё раз введенные данные"
)
MESSAGE_CAPTCHA_FAILED = (
    "Изображение собрано неверно. Соберите пазл правильно и повторите попытку."
)
MESSAGE_BLOCKED = "Вы заблокированы. Обратитесь к администратору"
MESSAGE_LOGIN_SUCCESS = "Вы успешно авторизовались"
MESSAGE_LOGIN_EXISTS = "Пользователь с таким логином уже существует."
