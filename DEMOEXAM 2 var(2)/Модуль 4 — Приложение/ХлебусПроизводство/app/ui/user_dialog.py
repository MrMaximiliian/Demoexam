"""Диалог добавления и редактирования учётной записи пользователя.

Диалог является модальным. После закрытия результат доступен в атрибуте
result в виде словаря с введёнными значениями либо None, если пользователь
отменил ввод.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app.ui import app_theme


class UserDialog(tk.Toplevel):
    def __init__(self, master, roles, user=None):
        super().__init__(master)
        self.roles = roles
        self.user = user
        self.is_edit_mode = user is not None
        self.result = None

        self.login_var = tk.StringVar(value=user.login if user else "")
        self.password_var = tk.StringVar()
        self.full_name_var = tk.StringVar(value=user.full_name if user else "")
        self.role_var = tk.StringVar()
        self.blocked_var = tk.BooleanVar(value=user.is_blocked if user else False)

        self.title("Изменение пользователя" if self.is_edit_mode else "Новый пользователь")
        self.configure(background=app_theme.SURFACE)
        self.resizable(False, False)
        self.transient(master)

        self._build_widgets()
        self._preselect_role()

        app_theme.center_window(self, 380, 360)
        self.grab_set()
        self.login_entry.focus_set()

    def _build_widgets(self):
        container = ttk.Frame(self, style="Surface.TFrame", padding=20)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)

        ttk.Label(container, text="Логин", style="Surface.TLabel").grid(
            row=0, column=0, sticky="w")
        self.login_entry = ttk.Entry(container, textvariable=self.login_var)
        self.login_entry.grid(row=1, column=0, sticky="ew", pady=(2, 12))
        if self.is_edit_mode:
            self.login_entry.configure(state="disabled")

        password_caption = "Пароль" if not self.is_edit_mode else "Новый пароль"
        ttk.Label(container, text=password_caption, style="Surface.TLabel").grid(
            row=2, column=0, sticky="w")
        self.password_entry = ttk.Entry(container, textvariable=self.password_var, show="•")
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=(2, 2))
        if self.is_edit_mode:
            ttk.Label(container, text="Оставьте пустым, чтобы не менять пароль",
                      style="Hint.TLabel").grid(row=4, column=0, sticky="w", pady=(0, 10))

        ttk.Label(container, text="ФИО", style="Surface.TLabel").grid(
            row=5, column=0, sticky="w")
        self.full_name_entry = ttk.Entry(container, textvariable=self.full_name_var)
        self.full_name_entry.grid(row=6, column=0, sticky="ew", pady=(2, 12))

        ttk.Label(container, text="Роль", style="Surface.TLabel").grid(
            row=7, column=0, sticky="w")
        self.role_combobox = ttk.Combobox(
            container, textvariable=self.role_var, state="readonly",
            values=[role.name for role in self.roles],
        )
        self.role_combobox.grid(row=8, column=0, sticky="ew", pady=(2, 12))

        if self.is_edit_mode:
            ttk.Checkbutton(container, text="Учётная запись заблокирована",
                            variable=self.blocked_var).grid(
                row=9, column=0, sticky="w", pady=(0, 12))

        buttons = ttk.Frame(container, style="Surface.TFrame")
        buttons.grid(row=10, column=0, sticky="e")
        ttk.Button(buttons, text="Отмена", command=self.destroy).grid(
            row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Сохранить", style="Accent.TButton",
                   command=self._on_save).grid(row=0, column=1)

    def _preselect_role(self):
        if self.user is not None:
            self.role_var.set(self.user.role_name)
        elif self.roles:
            self.role_var.set(self.roles[0].name)

    def _selected_role_id(self):
        for role in self.roles:
            if role.name == self.role_var.get():
                return role.id
        return None

    def _on_save(self):
        login = self.login_var.get().strip()
        password = self.password_var.get()
        role_id = self._selected_role_id()

        if not self.is_edit_mode and not login:
            messagebox.showwarning("Проверка данных", "Введите логин пользователя.", parent=self)
            return
        if " " in login:
            messagebox.showwarning("Проверка данных", "Логин не должен содержать пробелов.", parent=self)
            return
        if not self.is_edit_mode and not password:
            messagebox.showwarning("Проверка данных", "Введите пароль пользователя.", parent=self)
            return
        if role_id is None:
            messagebox.showwarning("Проверка данных", "Выберите роль пользователя.", parent=self)
            return

        self.result = {
            "login": login,
            "password": password,
            "full_name": self.full_name_var.get().strip(),
            "role_id": role_id,
            "is_blocked": bool(self.blocked_var.get()),
        }
        self.destroy()
