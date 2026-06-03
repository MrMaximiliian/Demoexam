-- =====================================================================
--  Модуль 3. Расчёт полной стоимости заказа покупателя.
--
--  Полная стоимость заказа складывается из стоимости материалов,
--  необходимых для производства заказанной продукции. Для каждой
--  строки заказа стоимость материалов на единицу продукции берётся из
--  спецификации (норма расхода материала, умноженная на цену материала)
--  и умножается на количество продукции в заказе.
-- =====================================================================

-- Запрос 1. Итоговая стоимость материалов по каждому заказу.
SELECT
    o.id                                         AS "Заказ",
    o.number                                     AS "Номер",
    o.order_date                                 AS "Дата",
    buyer.name                                   AS "Покупатель",
    ROUND(SUM(item.quantity * COALESCE(unit_cost.cost, 0)), 2) AS "Стоимость материалов, руб."
FROM orders AS o
JOIN counterparties AS buyer
    ON buyer.id = o.buyer_id
JOIN order_items AS item
    ON item.order_id = o.id
LEFT JOIN (
    SELECT
        s.product_id              AS product_id,
        SUM(s.consumption_rate * m.price) AS cost
    FROM specifications AS s
    JOIN materials AS m
        ON m.id = s.material_id
    GROUP BY s.product_id
) AS unit_cost
    ON unit_cost.product_id = item.product_id
GROUP BY o.id, o.number, o.order_date, buyer.name
ORDER BY o.id;


-- Запрос 2. Детализация расчёта по строкам конкретного заказа
-- (:order_id — идентификатор заказа, для которого выполняется расчёт).
SELECT
    o.number                                     AS "Номер заказа",
    p.name                                       AS "Продукция",
    item.quantity                                AS "Кол-во",
    ROUND(COALESCE(unit_cost.cost, 0), 2)        AS "Материалы на единицу, руб.",
    ROUND(item.quantity * COALESCE(unit_cost.cost, 0), 2) AS "Стоимость строки, руб."
FROM order_items AS item
JOIN orders AS o
    ON o.id = item.order_id
JOIN products AS p
    ON p.id = item.product_id
LEFT JOIN (
    SELECT
        s.product_id              AS product_id,
        SUM(s.consumption_rate * m.price) AS cost
    FROM specifications AS s
    JOIN materials AS m
        ON m.id = s.material_id
    GROUP BY s.product_id
) AS unit_cost
    ON unit_cost.product_id = item.product_id
WHERE o.id = :order_id
ORDER BY p.name;
