"""Репозиторий нормативно-справочной информации.

Предоставляет рабочим столам данные о продукции и заказах. Расчёт
стоимости материалов по заказу выполняется тем же запросом, что и в
Модуле 3 (стоимость материалов с учётом нормы расхода).
"""

from app.models import OrderSummary

ORDERS_WITH_COST = """
    SELECT o.id, o.number, o.order_date, buyer.name AS buyer,
           ROUND(SUM(item.quantity * COALESCE(unit_cost.cost, 0)), 2) AS material_cost
    FROM orders AS o
    JOIN counterparties AS buyer ON buyer.id = o.buyer_id
    JOIN order_items AS item ON item.order_id = o.id
    LEFT JOIN (
        SELECT s.product_id AS product_id,
               SUM(s.consumption_rate * m.price) AS cost
        FROM specifications AS s
        JOIN materials AS m ON m.id = s.material_id
        GROUP BY s.product_id
    ) AS unit_cost ON unit_cost.product_id = item.product_id
    GROUP BY o.id, o.number, o.order_date, buyer.name
    ORDER BY o.id
"""

PRODUCTS = """
    SELECT p.name, p.code, u.name AS unit, p.price
    FROM products AS p
    JOIN units AS u ON u.id = p.unit_id
    ORDER BY p.name
"""


class ReferenceRepository:
    def __init__(self, connection):
        self.connection = connection

    def list_orders_with_cost(self):
        rows = self.connection.query(ORDERS_WITH_COST)
        return [
            OrderSummary(
                row["id"], row["number"], row["order_date"],
                row["buyer"], row["material_cost"],
            )
            for row in rows
        ]

    def list_products(self):
        rows = self.connection.query(PRODUCTS)
        return [
            (row["name"], row["code"] or "—", row["unit"], row["price"])
            for row in rows
        ]
