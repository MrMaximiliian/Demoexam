"""Форма авторизации пользователя.

Форма собирает логин и пароль, проверяет прохождение капчи и передаёт
данные сервису аутентификации. По результату выводит соответствующее
сообщение, а при успешном входе — открывает рабочий стол.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app import config
from app.services import AuthStatus
from app.ui.captcha_frame import CaptchaFrame

STATUS_MESSAGES = {
    AuthStatus.EMPTY_FIELDS: ("Проверка данных", config.MESSAGE_EMPTY_FIELDS, "warning"),
    AuthStatus.WRONG_CREDENTIALS: ("Ошибка входа", config.MESSAGE_WRONG_CREDENTIALS, "error"),
    AuthStatus.CAPTCHA_FAILED: ("Капча", config.MESSAGE_CAPTCHA_FAILED, "error"),
    AuthStatus.BLOCKED: ("Доступ запрещён", config.MESSAGE_BLOCKED, "error"),
}


class LoginFrame(ttk.Frame):
    def __init__(self, master, auth_service, on_success):
        super().__init__(master, padding=24)
        self.auth_service = auth_service
        self.on_success = on_success

        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self._build_widgets()

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Surface.TFrame", padding=28)
        card.grid(row=0, column=0)

        ttk.Label(card, text="Информационная система производства",
                  style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(card, text=config.COMPANY_NAME,
                  style="Subtitle.TLabel").grid(row=1, column=0, columnspan=2,
                                                sticky="w", pady=(0, 18))

        ttk.Label(card, text="Логин", style="Surface.TLabel").grid(
            row=2, column=0, sticky="w")
        self.login_entry = ttk.Entry(card, textvariable=self.login_var, width=34)
        self.login_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 12))

        ttk.Label(card, text="Пароль", style="Surface.TLabel").grid(
            row=4, column=0, sticky="w")
        self.password_entry = ttk.Entry(card, textvariable=self.password_var,
                                        width=34, show="•")
        self.password_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(2, 18))

        self.captcha = CaptchaFrame(card)
        self.captcha.grid(row=6, column=0, columnspan=2, pady=(0, 18))

        self.login_button = ttk.Button(card, text="Войти", style="Accent.TButton",
                                       command=self.try_login)
        self.login_button.grid(row=7, column=0, columnspan=2, sticky="ew")

        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        self.login_entry.focus_set()
        self.bind_all("<Return>", lambda event: self.try_login())

    def try_login(self):
        login = self.login_var.get().strip()
        password = self.password_var.get()

        if not login or not password:
            messagebox.showwarning("Проверка данных", config.MESSAGE_EMPTY_FIELDS)
            self._highlight_empty(login, password)
            return

        result = self.auth_service.authenticate(
            login, password, captcha_passed=self.captcha.is_solved()
        )

        if result.is_success:
            messagebox.showinfo("Авторизация", config.MESSAGE_LOGIN_SUCCESS)
            self.unbind_all("<Return>")
            self.on_success(result.user)
            return

        title, text, icon = STATUS_MESSAGES[result.status]
        if icon == "error":
            messagebox.showerror(title, text)
        else:
            messagebox.showwarning(title, text)

        if result.status in (AuthStatus.WRONG_CREDENTIALS, AuthStatus.CAPTCHA_FAILED,
                              AuthStatus.BLOCKED):
            self.password_var.set("")
            self.captcha.shuffle()
            self.password_entry.focus_set()

    def _highlight_empty(self, login, password):
        target = self.login_entry if not login else self.password_entry
        target.focus_set()
