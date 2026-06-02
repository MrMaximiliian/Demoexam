# -*- coding: utf-8 -*-
# Рабочий стол администратора: управление пользователями

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc

from config import APP_TITLE
from database.user_repository import UserRepository
from forms.user_dialog import UserDialog


class AdminForm(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.repository = UserRepository()
        self.title(f"{APP_TITLE} — Панель администратора")
        self.minsize(560, 380)
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self._build_widgets()
        self.load_users()

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        tk.Label(self, text="Управление пользователями",
                 font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, pady=8)

        columns = ("id", "логин", "роль", "блокировка")
        self.users_table = ttk.Treeview(self, columns=columns,
                                        show="headings")
        headers = {"id": "ID", "логин": "Логин",
                   "роль": "Роль", "блокировка": "Блокировка"}
        for column in columns:
            self.users_table.heading(column, text=headers[column])
            self.users_table.column(column, anchor="center", width=120)
        self.users_table.grid(row=1, column=0, sticky="nsew",
                              padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self, orient="vertical",
                                  command=self.users_table.yview)
        self.users_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))

        actions = tk.LabelFrame(self, text="Действия", padx=10, pady=8)
        actions.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        tk.Button(actions, text="Добавить", width=14,
                  command=self.add_user).grid(row=0, column=0, padx=5)
        tk.Button(actions, text="Изменить", width=14,
                  command=self.edit_user).grid(row=0, column=1, padx=5)
        tk.Button(actions, text="Выход", width=14,
                  command=self._exit).grid(row=0, column=2, padx=5)

    def load_users(self):
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        try:
            for user in self.repository.get_all():
                self.users_table.insert(
                    "", "end", iid=user.user_id,
                    values=(user.user_id, user.login, user.role,
                            "Да" if user.blocked else "Нет"))
        except pyodbc.Error:
            messagebox.showerror(
                "Ошибка базы данных",
                "Не удалось загрузить список пользователей.")

    def add_user(self):
        UserDialog(self, self.repository)

    def edit_user(self):
        selection = self.users_table.selection()
        if not selection:
            messagebox.showwarning(
                "Внимание", "Выберите пользователя в списке.")
            return
        user_id = int(selection[0])
        editable = next(
            (user for user in self.repository.get_all()
             if user.user_id == user_id), None)
        if editable is not None:
            UserDialog(self, self.repository, user=editable)

    def _exit(self):
        self.destroy()
        self.master.destroy()
