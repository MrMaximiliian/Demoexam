"""Повторно используемые табличные представления данных.

Вкладки с заказами и продукцией одинаковы на рабочих столах администратора
и пользователя, поэтому вынесены в отдельный модуль визуальных компонентов.
Таблицы растягиваются вместе с окном за счёт весов строк и столбцов.
"""

from tkinter import ttk


def _make_tree(parent, columns):
    container = ttk.Frame(parent, padding=12)
    container.columnconfigure(0, weight=1)
    container.rowconfigure(0, weight=1)

    tree = ttk.Treeview(container, columns=[key for key, _, _ in columns],
                        show="headings", selectmode="browse")
    for key, heading, width in columns:
        anchor = "e" if key in ("price", "cost") else "w"
        tree.heading(key, text=heading)
        tree.column(key, width=width, anchor=anchor, stretch=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    return container, tree


def build_orders_tab(notebook, reference_repository):
    columns = [
        ("number", "Номер заказа", 120),
        ("date", "Дата", 130),
        ("buyer", "Покупатель", 280),
        ("cost", "Стоимость материалов, ₽", 200),
    ]
    container, tree = _make_tree(notebook, columns)
    for order in reference_repository.list_orders_with_cost():
        tree.insert("", "end", values=(
            order.number, order.order_date, order.buyer, order.material_cost_text
        ))
    return container


def build_products_tab(notebook, reference_repository):
    columns = [
        ("name", "Наименование", 280),
        ("code", "Код", 140),
        ("unit", "Ед. изм.", 100),
        ("price", "Цена, ₽", 120),
    ]
    container, tree = _make_tree(notebook, columns)
    for name, code, unit, price in reference_repository.list_products():
        tree.insert("", "end", values=(name, code, unit, "{0:.2f}".format(price)))
    return container
