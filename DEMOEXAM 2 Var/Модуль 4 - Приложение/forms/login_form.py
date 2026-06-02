# -*- coding: utf-8 -*-
# Форма авторизации пользователей

import tkinter as tk
from tkinter import messagebox

import pyodbc

from config import APP_TITLE, LOGIN_MAX_LENGTH
from database.user_repository import UserRepository
from components.captcha_widget import CaptchaWidget
from forms.admin_form import AdminForm
from forms.user_desktop_form import UserDesktopForm

WRONG_CREDENTIALS_MESSAGE = ("Вы ввели неверный логин или пароль. "
                             "Пожалуйста проверьте ещё раз введенные данные.")
BLOCKED_MESSAGE = "Вы заблокированы. Обратитесь к администратору."


class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.repository = UserRepository()
        self.title(f"{APP_TITLE} — Авторизация")
        self.minsize(360, 470)
        self.report_callback_exception = self._show_unexpected_error
        self._build_widgets()

    def _build_widgets(self):
        length_validator = (self.register(self._limit_length), "%P", "%d")

        container = tk.Frame(self, padx=20, pady=15)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Вход в систему",
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        credentials = tk.LabelFrame(container, text="Учётные данные",
                                    padx=10, pady=10)
        credentials.pack(fill="x")

        tk.Label(credentials, text="Логин:").grid(row=0, column=0,
                                                  sticky="e", pady=4)
        self.login_entry = tk.Entry(credentials, width=25, validate="key",
                                    validatecommand=length_validator)
        self.login_entry.grid(row=0, column=1, pady=4)

        tk.Label(credentials, text="Пароль:").grid(row=1, column=0,
                                                   sticky="e", pady=4)
        self.password_entry = tk.Entry(credentials, width=25, show="*",
                                       validate="key",
                                       validatecommand=length_validator)
        self.password_entry.grid(row=1, column=1, pady=4)

        captcha_group = tk.LabelFrame(container, text="Соберите изображение",
                                      padx=10, pady=10)
        captcha_group.pack(fill="x", pady=(10, 0))
        self.captcha = CaptchaWidget(captcha_group)
        self.captcha.pack()

        tk.Button(container, text="Войти", width=20,
                  command=self.login).pack(pady=(12, 0))

        self.login_entry.focus_set()

    def _limit_length(self, proposed_value, action):
        if action != "1":
            return True
        return len(proposed_value) <= LOGIN_MAX_LENGTH

    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            messagebox.showwarning(
                "Внимание",
                "Поля «Логин» и «Пароль» обязательны для заполнения.")
            return

        try:
            user = self.repository.find_by_login(login)

            if user is None:
                messagebox.showerror("Ошибка", WRONG_CREDENTIALS_MESSAGE)
                return

            if user.blocked:
                messagebox.showerror("Доступ запрещён", BLOCKED_MESSAGE)
                return

            if not self.captcha.is_solved():
                self._handle_failed_attempt(
                    user, "Изображение собрано неверно. Попробуйте ещё раз.")
                return

            if password != user.password:
                self._handle_failed_attempt(user, WRONG_CREDENTIALS_MESSAGE)
                return

            self.repository.reset_attempts(user)
            messagebox.showinfo("Успех", "Вы успешно авторизовались.")
            self._open_desktop(user)
        except pyodbc.Error:
            messagebox.showerror(
                "Ошибка базы данных",
                "Не удалось обратиться к базе данных. Проверьте подключение "
                "к серверу.")

    def _handle_failed_attempt(self, user, error_message):
        blocked = self.repository.register_failed_attempt(user)
        if blocked:
            messagebox.showerror("Доступ запрещён", BLOCKED_MESSAGE)
        else:
            messagebox.showerror("Ошибка", error_message)
        self.captcha.shuffle()

    def _open_desktop(self, user):
        self.withdraw()
        if user.is_admin():
            AdminForm(self, user)
        else:
            UserDesktopForm(self, user)

    def _show_unexpected_error(self, exception_type, value, traceback):
        messagebox.showerror(
            "Ошибка",
            f"Произошла непредвиденная ошибка:\n{value}")
