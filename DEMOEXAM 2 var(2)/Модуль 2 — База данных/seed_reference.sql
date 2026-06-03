-- =====================================================================
--  Модуль 2. Заполнение справочников нормативно-справочной информацией.
--  Данные взяты из приложенных документов заказчика
--  (Цены.xlsx, Спецификация.xlsx, Производство.xlsx).
-- =====================================================================

PRAGMA foreign_keys = ON;

INSERT INTO units (name) VALUES ('шт'), ('кг');

INSERT INTO roles (name) VALUES ('Администратор'), ('Пользователь');

INSERT INTO materials (code, name, unit_id, price) VALUES
    (NULL,          'Закваска сметанная',      (SELECT id FROM units WHERE name = 'кг'),  45),
    ('НФ-00000020', 'Изюм',                    (SELECT id FROM units WHERE name = 'кг'),  150),
    ('НФ-00000021', 'Масло сливочное',         (SELECT id FROM units WHERE name = 'кг'),  124),
    ('НФ-00000004', 'Молоко нормализованное',  (SELECT id FROM units WHERE name = 'кг'),  34),
    ('НФ-00000018', 'Мука',                    (SELECT id FROM units WHERE name = 'кг'),  220),
    ('НФ-00000019', 'Сода',                    (SELECT id FROM units WHERE name = 'шт'),  60),
    ('НФ-00000022', 'Яйца',                    (SELECT id FROM units WHERE name = 'шт'),  80);

INSERT INTO products (code, name, unit_id, price) VALUES
    (NULL,          'Батон нарезной',          (SELECT id FROM units WHERE name = 'шт'),  45),
    ('НФ-00000014', 'Булочка с изюмом',        (SELECT id FROM units WHERE name = 'шт'),  35),
    (NULL,          'Булочка с корицей',       (SELECT id FROM units WHERE name = 'шт'),  35),
    (NULL,          'Хлеб белый 1 кг.',        (SELECT id FROM units WHERE name = 'шт'),  42),
    (NULL,          'Хлеб Кронштадтский 1 кг.',(SELECT id FROM units WHERE name = 'шт'),  120),
    (NULL,          'Хлеб ржаной 800г.',       (SELECT id FROM units WHERE name = 'шт'),  47);

-- Спецификация продукции "Булочка с изюмом": норма расхода материалов
-- на одну единицу готовой продукции.
INSERT INTO specifications (product_id, material_id, consumption_rate) VALUES
    ((SELECT id FROM products  WHERE name = 'Булочка с изюмом'),
     (SELECT id FROM materials WHERE name = 'Изюм'),                   0.02),
    ((SELECT id FROM products  WHERE name = 'Булочка с изюмом'),
     (SELECT id FROM materials WHERE name = 'Масло сливочное'),        0.02),
    ((SELECT id FROM products  WHERE name = 'Булочка с изюмом'),
     (SELECT id FROM materials WHERE name = 'Молоко нормализованное'), 0.15),
    ((SELECT id FROM products  WHERE name = 'Булочка с изюмом'),
     (SELECT id FROM materials WHERE name = 'Яйца'),                   0.25),
    ((SELECT id FROM products  WHERE name = 'Булочка с изюмом'),
     (SELECT id FROM materials WHERE name = 'Мука'),                   0.1),
    ((SELECT id FROM products  WHERE name = 'Булочка с изюмом'),
     (SELECT id FROM materials WHERE name = 'Сода'),                   0.005);
