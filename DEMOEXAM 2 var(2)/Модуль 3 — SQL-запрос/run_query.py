"""Демонстрация запроса расчёта стоимости заказа (Модуль 3).

Скрипт подключается к базе данных hlebus.db и выводит итоговую стоимость
материалов по каждому заказу, а также детализацию по выбранному заказу.

Запуск:  python run_query.py [идентификатор_заказа]
"""

import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hlebus.db")

TOTAL_QUERY = """
SELECT o.id, o.number, o.order_date, buyer.name,
       ROUND(SUM(item.quantity * COALESCE(unit_cost.cost, 0)), 2)
FROM orders AS o
JOIN counterparties AS buyer ON buyer.id = o.buyer_id
JOIN order_items AS item ON item.order_id = o.id
LEFT JOIN (
    SELECT s.product_id AS product_id, SUM(s.consumption_rate * m.price) AS cost
    FROM specifications AS s
    JOIN materials AS m ON m.id = s.material_id
    GROUP BY s.product_id
) AS unit_cost ON unit_cost.product_id = item.product_id
GROUP BY o.id, o.number, o.order_date, buyer.name
ORDER BY o.id
"""

DETAIL_QUERY = """
SELECT o.number, p.name, item.quantity,
       ROUND(COALESCE(unit_cost.cost, 0), 2),
       ROUND(item.quantity * COALESCE(unit_cost.cost, 0), 2)
FROM order_items AS item
JOIN orders AS o ON o.id = item.order_id
JOIN products AS p ON p.id = item.product_id
LEFT JOIN (
    SELECT s.product_id AS product_id, SUM(s.consumption_rate * m.price) AS cost
    FROM specifications AS s
    JOIN materials AS m ON m.id = s.material_id
    GROUP BY s.product_id
) AS unit_cost ON unit_cost.product_id = item.product_id
WHERE o.id = ?
ORDER BY p.name
"""


def main():
    order_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    connection = sqlite3.connect(DB_PATH)
    try:
        print("Полная стоимость материалов по заказам:")
        print("-" * 70)
        for row in connection.execute(TOTAL_QUERY):
            print("Заказ №{1} от {2}, покупатель {3:30} {4:>12} руб.".format(*row))

        print("\nДетализация по заказу id =", order_id)
        print("-" * 70)
        for number, name, quantity, unit_cost, line_cost in connection.execute(
            DETAIL_QUERY, (order_id,)
        ):
            print("{0:32} {1:>8} x {2:>8} = {3:>12} руб.".format(
                name, quantity, unit_cost, line_cost))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
