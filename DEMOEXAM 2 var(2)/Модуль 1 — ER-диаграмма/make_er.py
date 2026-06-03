# -*- coding: utf-8 -*-
"""Генерация ER-диаграммы ИС производства ООО "Хлебус" (Модуль 1)."""

import subprocess

HEADER = "#2F4858"
PK_BG = "#DCE7F1"
FK_MARK = "#8A5A00"

entities = {
    "units": ("Единицы измерения (units)", [
        ("PK", "id"), ("", "name"),
    ]),
    "roles": ("Роли (roles)", [
        ("PK", "id"), ("", "name"),
    ]),
    "counterparties": ("Контрагенты (counterparties)", [
        ("PK", "id"), ("", "code"), ("", "name"), ("", "inn"),
        ("", "address"), ("", "phone"), ("", "is_supplier"), ("", "is_buyer"),
    ]),
    "materials": ("Материалы (materials)", [
        ("PK", "id"), ("", "code"), ("", "name"),
        ("FK", "unit_id"), ("", "price"),
    ]),
    "products": ("Продукция (products)", [
        ("PK", "id"), ("", "code"), ("", "name"),
        ("FK", "unit_id"), ("", "price"),
    ]),
    "specifications": ("Спецификация (specifications)", [
        ("PK", "id"), ("FK", "product_id"), ("FK", "material_id"),
        ("", "consumption_rate"),
    ]),
    "orders": ("Заказы (orders)", [
        ("PK", "id"), ("", "number"), ("", "order_date"),
        ("FK", "buyer_id"), ("FK", "executor_id"),
    ]),
    "order_items": ("Строки заказа (order_items)", [
        ("PK", "id"), ("FK", "order_id"), ("FK", "product_id"),
        ("", "quantity"), ("", "price"),
    ]),
    "users": ("Пользователи (users)", [
        ("PK", "id"), ("", "login"), ("", "password_hash"),
        ("", "full_name"), ("FK", "role_id"),
        ("", "is_blocked"), ("", "failed_attempts"),
    ]),
}

# (child, child_field) -> (parent, parent_field)
relations = [
    ("materials", "unit_id", "units", "id"),
    ("products", "unit_id", "units", "id"),
    ("specifications", "product_id", "products", "id"),
    ("specifications", "material_id", "materials", "id"),
    ("order_items", "order_id", "orders", "id"),
    ("order_items", "product_id", "products", "id"),
    ("orders", "buyer_id", "counterparties", "id"),
    ("orders", "executor_id", "counterparties", "id"),
    ("users", "role_id", "roles", "id"),
]


def build_node(name, title, fields):
    rows = [
        '<TR><TD PORT="title" COLSPAN="2" BGCOLOR="{0}">'
        '<FONT COLOR="white" POINT-SIZE="12"><B>{1}</B></FONT></TD></TR>'.format(HEADER, title)
    ]
    for mark, field in fields:
        is_pk = mark == "PK"
        bg = ' BGCOLOR="{0}"'.format(PK_BG) if is_pk else ""
        if mark == "FK":
            marker = '<FONT COLOR="{0}"><B>FK</B></FONT>'.format(FK_MARK)
        elif mark == "PK":
            marker = "<B>PK</B>"
        else:
            marker = " "
        value = "<B>{0}</B>".format(field) if is_pk else field
        rows.append(
            '<TR><TD ALIGN="CENTER"{2}>{0}</TD>'
            '<TD PORT="{3}" ALIGN="LEFT"{2}>{1}</TD></TR>'.format(marker, value, bg, field)
        )
    label = (
        '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5">'
        + "".join(rows)
        + "</TABLE>>"
    )
    return '  {0} [label={1}];'.format(name, label)


def main():
    lines = [
        "digraph er {",
        "  graph [rankdir=LR, splines=spline, nodesep=0.6, ranksep=1.1, "
        'bgcolor="white", pad=0.4, fontname="DejaVu Sans"];',
        '  node [shape=plaintext, fontname="DejaVu Sans", fontsize=11];',
        '  edge [color="#41566B", penwidth=1.3, fontname="DejaVu Sans", '
        'fontsize=10, arrowhead=crow, arrowtail=none, dir=both];',
        "",
        '  label=<<FONT POINT-SIZE="18"><B>ER-диаграмма информационной системы '
        "производства ООО «Хлебус»</B></FONT>>;",
        "  labelloc=t;",
        "",
    ]
    for name, (title, fields) in entities.items():
        lines.append(build_node(name, title, fields))
    lines.append("")
    for child, child_field, parent, parent_field in relations:
        lines.append(
            '  {0}:{1} -> {2}:{3} [taillabel="N", headlabel="1"];'.format(
                child, child_field, parent, parent_field
            )
        )
    lines.append("}")
    dot = "\n".join(lines)
    with open("er.dot", "w", encoding="utf-8") as handle:
        handle.write(dot)
    subprocess.run(["dot", "-Tpdf", "er.dot", "-o", "ER-диаграмма.pdf"], check=True)
    subprocess.run(["dot", "-Tpng", "-Gdpi=130", "er.dot", "-o", "er_preview.png"], check=True)
    print("ER-диаграмма создана")


if __name__ == "__main__":
    main()
