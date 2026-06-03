-- =====================================================================
--  Информационная система производства ООО "Хлебус"
--  Модуль 2. Создание схемы базы данных (SQLite)
--
--  Схема приведена к 3НФ. Ссылочная целостность обеспечивается
--  внешними ключами. Для контроля корректности значений добавлены
--  ограничения UNIQUE и CHECK.
-- =====================================================================

PRAGMA foreign_keys = ON;

-- Единицы измерения вынесены в отдельный справочник, чтобы исключить
-- дублирование строковых значений ("шт", "кг") в продукции и материалах.
CREATE TABLE units (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Роли пользователей системы.
CREATE TABLE roles (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Контрагенты предприятия. Один контрагент может быть одновременно
-- поставщиком и покупателем, поэтому признаки хранятся отдельными флагами.
CREATE TABLE counterparties (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT,
    name        TEXT NOT NULL,
    inn         TEXT,
    address     TEXT,
    phone       TEXT,
    is_supplier INTEGER NOT NULL DEFAULT 0 CHECK (is_supplier IN (0, 1)),
    is_buyer    INTEGER NOT NULL DEFAULT 0 CHECK (is_buyer IN (0, 1))
);

-- Сырьё и материалы, из которых изготавливается продукция.
CREATE TABLE materials (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    code    TEXT,
    name    TEXT NOT NULL UNIQUE,
    unit_id INTEGER NOT NULL REFERENCES units (id),
    price   REAL NOT NULL CHECK (price >= 0)
);

-- Готовая продукция предприятия.
CREATE TABLE products (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    code    TEXT,
    name    TEXT NOT NULL UNIQUE,
    unit_id INTEGER NOT NULL REFERENCES units (id),
    price   REAL CHECK (price >= 0)
);

-- Спецификация — состав продукции. Разрешает связь "многие-ко-многим"
-- между продукцией и материалами и хранит норму расхода материала
-- на единицу продукции.
CREATE TABLE specifications (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id       INTEGER NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    material_id      INTEGER NOT NULL REFERENCES materials (id),
    consumption_rate REAL NOT NULL CHECK (consumption_rate > 0),
    UNIQUE (product_id, material_id)
);

-- Заказы покупателей (шапка документа).
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    number      TEXT NOT NULL,
    order_date  TEXT NOT NULL,
    buyer_id    INTEGER NOT NULL REFERENCES counterparties (id),
    executor_id INTEGER REFERENCES counterparties (id)
);

-- Строки заказа (табличная часть документа).
CREATE TABLE order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products (id),
    quantity   REAL NOT NULL CHECK (quantity > 0),
    price      REAL CHECK (price >= 0),
    UNIQUE (order_id, product_id)
);

-- Учётные записи пользователей информационной системы.
-- failed_attempts хранит число подряд идущих неудачных попыток входа,
-- is_blocked — признак блокировки учётной записи.
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    login           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    full_name       TEXT,
    role_id         INTEGER NOT NULL REFERENCES roles (id),
    is_blocked      INTEGER NOT NULL DEFAULT 0 CHECK (is_blocked IN (0, 1)),
    failed_attempts INTEGER NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0)
);

CREATE INDEX idx_specifications_product  ON specifications (product_id);
CREATE INDEX idx_order_items_order       ON order_items (order_id);
CREATE INDEX idx_orders_buyer            ON orders (buyer_id);
