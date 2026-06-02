# -*- coding: utf-8 -*-
# Окно добавления и изменения пользователя

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc

from config import LOGIN_MAX_LENGTH
from models.user import User

ROLES = ["Администратор", "Пользователь"]


class UserDialog(tk.Toplevel):
    def __init__(self, master, repository, user=None):
        super().__init__(master)
        self.master = master
        self.repository = repository
        self.editable_user = user
        is_new = user is None
        self.title("Новый пользователь" if is_new else "Изменение пользователя")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._build_widgets()

    def _build_widgets(self):
        length_validator = (self.register(self._limit_length), "%P", "%d")

        form = tk.Frame(self, padx=15, pady=15)
        form.pack()

        tk.Label(form, text="Логин:").grid(row=0, column=0, sticky="e", pady=4)
        self.login_entry = tk.Entry(form, width=25, validate="key",
                                    validatecommand=length_validator)
        self.login_entry.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Пароль:").grid(row=1, column=0, sticky="e", pady=4)
        self.password_entry = tk.Entry(form, width=25, validate="key",
                                       validatecommand=length_validator)
        self.password_entry.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Роль:").grid(row=2, column=0, sticky="e", pady=4)
        self.role_box = ttk.Combobox(form, width=22, state="readonly",
                                     values=ROLES)
        self.role_box.grid(row=2, column=1, pady=4)
        self.role_box.current(1)

        self.blocked_var = tk.IntVar()
        blocked_checkbox = tk.Checkbutton(form, text="Заблокирован",
                                          variable=self.blocked_var)

        if self.editable_user is not None:
            self.login_entry.insert(0, self.editable_user.login)
            self.password_entry.insert(0, self.editable_user.password)
            self.role_box.set(self.editable_user.role)
            self.blocked_var.set(1 if self.editable_user.blocked else 0)
            blocked_checkbox.grid(row=3, column=1, sticky="w", pady=4)

        tk.Button(form, text="Сохранить", width=20,
                  command=self.save).grid(row=4, column=0, columnspan=2,
                                          pady=(10, 0))
        self.login_entry.focus_set()

    def _limit_length(self, proposed_value, action):
        if action != "1":
            return True
        return len(proposed_value) <= LOGIN_MAX_LENGTH

    def save(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_box.get()

        if not login or not password:
            messagebox.showwarning(
                "Внимание", "Поля «Логин» и «Пароль» обязательны для заполнения.")
            return

        try:
            if self.editable_user is None:
                if self.repository.exists(login):
                    messagebox.showerror(
                        "Ошибка",
                        "Пользователь с таким логином уже существует.")
                    return
                self.repository.add(login, password, role)
            else:
                self.editable_user.login = login
                self.editable_user.password = password
                self.editable_user.role = role
                self.editable_user.blocked = bool(self.blocked_var.get())
                self.repository.update(self.editable_user)
        except pyodbc.Error:
            messagebox.showerror(
                "Ошибка базы данных",
                "Не удалось сохранить данные пользователя.")
            return

        self.master.load_users()
        self.destroy()
