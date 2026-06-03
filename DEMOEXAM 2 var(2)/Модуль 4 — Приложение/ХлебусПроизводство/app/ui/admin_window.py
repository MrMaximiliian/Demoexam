"""Рабочий стол администратора.

Предоставляет управление учётными записями (добавление, изменение, снятие
блокировки) и просмотр производственных данных — заказов с расчётной
стоимостью материалов и справочника продукции.
"""

from tkinter import messagebox, ttk

from app import config
from app.ui import app_theme, data_views
from app.ui.user_dialog import UserDialog

USER_COLUMNS = [
    ("login", "Логин", 150),
    ("full_name", "ФИО", 240),
    ("role", "Роль", 150),
    ("status", "Статус", 130),
    ("attempts", "Попыток", 90),
]


class AdminFrame(ttk.Frame):
    def __init__(self, master, user_repository, reference_repository, password_hasher,
                 current_user, on_logout):
        super().__init__(master)
        self.user_repository = user_repository
        self.reference_repository = reference_repository
        self.password_hasher = password_hasher
        self.current_user = current_user
        self.on_logout = on_logout
        self._users_by_id = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_notebook()
        self.refresh_users()

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Управление информационной системой «Хлебус»",
                  style="HeaderTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header,
                  text="Администратор: {0}".format(self.current_user.display_name),
                  style="HeaderInfo.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(header, text="Выйти", command=self.on_logout).grid(
            row=0, column=1, rowspan=2, sticky="e")

    def _build_notebook(self):
        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)

        notebook.add(self._build_users_tab(notebook), text="Пользователи")
        notebook.add(data_views.build_orders_tab(notebook, self.reference_repository),
                     text="Заказы")
        notebook.add(data_views.build_products_tab(notebook, self.reference_repository),
                     text="Продукция")

    def _build_users_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=12)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(tab)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Button(toolbar, text="Добавить", style="Accent.TButton",
                   command=self._add_user).pack(side="left")
        ttk.Button(toolbar, text="Изменить", command=self._edit_user).pack(
            side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Снять блокировку", command=self._unblock_user).pack(
            side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Обновить", command=self.refresh_users).pack(
            side="left", padx=(8, 0))

        self.users_tree = ttk.Treeview(
            tab, columns=[key for key, _, _ in USER_COLUMNS],
            show="headings", selectmode="browse",
        )
        for key, heading, width in USER_COLUMNS:
            anchor = "center" if key == "attempts" else "w"
            self.users_tree.heading(key, text=heading)
            self.users_tree.column(key, width=width, anchor=anchor, stretch=True)
        self.users_tree.tag_configure("blocked", foreground="#C62828")

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        self.users_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.users_tree.bind("<Double-1>", lambda event: self._edit_user())
        return tab

    def refresh_users(self):
        self.users_tree.delete(*self.users_tree.get_children())
        self._users_by_id = {}
        for user in self.user_repository.list_users():
            self._users_by_id[str(user.id)] = user
            tags = ("blocked",) if user.is_blocked else ()
            self.users_tree.insert(
                "", "end", iid=str(user.id), tags=tags,
                values=(user.login, user.full_name or "—", user.role_name,
                        user.status_text, user.failed_attempts),
            )

    def _selected_user(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showinfo("Выбор пользователя",
                                "Выберите запись в списке пользователей.")
            return None
        return self._users_by_id.get(selection[0])

    def _add_user(self):
        dialog = UserDialog(self, self.user_repository.list_roles())
        self.wait_window(dialog)
        if dialog.result is None:
            return

        data = dialog.result
        if self.user_repository.login_exists(data["login"]):
            messagebox.showerror("Добавление пользователя", config.MESSAGE_LOGIN_EXISTS)
            return

        password_hash = self.password_hasher.hash(data["login"], data["password"])
        self.user_repository.create_user(
            data["login"], password_hash, data["full_name"], data["role_id"]
        )
        self.refresh_users()
        messagebox.showinfo("Добавление пользователя",
                            "Пользователь «{0}» добавлен.".format(data["login"]))

    def _edit_user(self):
        user = self._selected_user()
        if user is None:
            return

        dialog = UserDialog(self, self.user_repository.list_roles(), user=user)
        self.wait_window(dialog)
        if dialog.result is None:
            return

        data = dialog.result
        self.user_repository.update_user(
            user.id, data["full_name"], data["role_id"], data["is_blocked"]
        )
        if data["password"]:
            new_hash = self.password_hasher.hash(user.login, data["password"])
            self.user_repository.change_password(user.id, new_hash)
        self.refresh_users()
        messagebox.showinfo("Изменение пользователя", "Изменения сохранены.")

    def _unblock_user(self):
        user = self._selected_user()
        if user is None:
            return
        if not user.is_blocked:
            messagebox.showinfo("Снятие блокировки",
                                "Учётная запись «{0}» не заблокирована.".format(user.login))
            return
        self.user_repository.unblock(user.id)
        self.refresh_users()
        messagebox.showinfo("Снятие блокировки",
                            "Блокировка с «{0}» снята.".format(user.login))
