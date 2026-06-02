# -*- coding: utf-8 -*-
# Рабочий стол пользователя с ролью "Пользователь"

import tkinter as tk

from config import APP_TITLE


class UserDesktopForm(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.title(f"{APP_TITLE} — Рабочий стол")
        self.minsize(400, 220)
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self._build_widgets()

    def _build_widgets(self):
        container = tk.Frame(self, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text=f"Добро пожаловать, {self.user.login}!",
                 font=("Segoe UI", 13)).pack(pady=(20, 5))
        tk.Label(container, text="Роль: Пользователь").pack()
        tk.Button(container, text="Выход", width=15,
                  command=self._exit).pack(pady=20)

    def _exit(self):
        self.destroy()
        self.master.destroy()
