"""Рабочий стол пользователя с ролью «Пользователь».

Доступен просмотр производственных данных без возможности управления
учётными записями: заказы с расчётной стоимостью материалов и справочник
продукции.
"""

from tkinter import ttk

from app.ui import data_views


class UserFrame(ttk.Frame):
    def __init__(self, master, reference_repository, current_user, on_logout):
        super().__init__(master)
        self.reference_repository = reference_repository
        self.current_user = current_user
        self.on_logout = on_logout

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_notebook()

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Информационная система «Хлебус»",
                  style="HeaderTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header,
                  text="Пользователь: {0}".format(self.current_user.display_name),
                  style="HeaderInfo.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(header, text="Выйти", command=self.on_logout).grid(
            row=0, column=1, rowspan=2, sticky="e")

    def _build_notebook(self):
        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        notebook.add(data_views.build_orders_tab(notebook, self.reference_repository),
                     text="Заказы")
        notebook.add(data_views.build_products_tab(notebook, self.reference_repository),
                     text="Продукция")
