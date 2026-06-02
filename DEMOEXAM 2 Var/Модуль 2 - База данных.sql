/* =====================================================================
   Модуль 2. Разработка базы данных на основании ER-диаграммы
   СУБД: Microsoft SQL Server
   ===================================================================== */

-- Создание базы данных
IF DB_ID(N'Хлебокомбинат') IS NULL
    CREATE DATABASE Хлебокомбинат;
GO

USE Хлебокомбинат;
GO

-- Если запускаем повторно, чистим таблицы (в порядке зависимостей)
IF OBJECT_ID(N'Состав_производства','U') IS NOT NULL DROP TABLE Состав_производства;
IF OBJECT_ID(N'Производство','U')        IS NOT NULL DROP TABLE Производство;
IF OBJECT_ID(N'Строка_заказа','U')       IS NOT NULL DROP TABLE Строка_заказа;
IF OBJECT_ID(N'Заказ','U')               IS NOT NULL DROP TABLE Заказ;
IF OBJECT_ID(N'Спецификация','U')        IS NOT NULL DROP TABLE Спецификация;
IF OBJECT_ID(N'Продукция','U')           IS NOT NULL DROP TABLE Продукция;
IF OBJECT_ID(N'Материал','U')            IS NOT NULL DROP TABLE Материал;
IF OBJECT_ID(N'Заказчик','U')            IS NOT NULL DROP TABLE Заказчик;
IF OBJECT_ID(N'Единица_измерения','U')   IS NOT NULL DROP TABLE Единица_измерения;
IF OBJECT_ID(N'Пользователи','U')        IS NOT NULL DROP TABLE Пользователи;
GO

/* ---------------------------------------------------------------------
   Справочники
--------------------------------------------------------------------- */
CREATE TABLE Единица_измерения (
    id_ед_изм    INT IDENTITY(1,1) PRIMARY KEY,
    наименование NVARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE Заказчик (
    id_заказчика       NVARCHAR(9) PRIMARY KEY,   -- код из файла Заказчики.json
    наименование       NVARCHAR(150) NOT NULL,
    ИНН                NVARCHAR(12) NULL,
    адрес              NVARCHAR(200) NULL,
    телефон            NVARCHAR(20) NULL,
    признак_продавец   BIT NOT NULL DEFAULT 0,
    признак_покупатель BIT NOT NULL DEFAULT 0
);

CREATE TABLE Продукция (
    id_продукции INT IDENTITY(1,1) PRIMARY KEY,
    код          NVARCHAR(20) NULL,
    наименование NVARCHAR(150) NOT NULL,
    цена         DECIMAL(10,2) NOT NULL DEFAULT 0,
    id_ед_изм    INT NOT NULL,
    CONSTRAINT FK_Продукция_ЕдИзм FOREIGN KEY (id_ед_изм)
        REFERENCES Единица_измерения(id_ед_изм)
);

CREATE TABLE Материал (
    id_материала INT IDENTITY(1,1) PRIMARY KEY,
    код          NVARCHAR(20) NULL,
    наименование NVARCHAR(150) NOT NULL,
    цена         DECIMAL(10,2) NOT NULL DEFAULT 0,
    id_ед_изм    INT NOT NULL,
    CONSTRAINT FK_Материал_ЕдИзм FOREIGN KEY (id_ед_изм)
        REFERENCES Единица_измерения(id_ед_изм)
);

/* ---------------------------------------------------------------------
   Спецификация (рецептура): какие материалы и сколько идёт на продукцию
--------------------------------------------------------------------- */
CREATE TABLE Спецификация (
    id_спецификации INT IDENTITY(1,1) PRIMARY KEY,
    id_продукции    INT NOT NULL,
    id_материала    INT NOT NULL,
    норма_расхода   DECIMAL(10,4) NOT NULL,
    CONSTRAINT FK_Спец_Продукция FOREIGN KEY (id_продукции)
        REFERENCES Продукция(id_продукции),
    CONSTRAINT FK_Спец_Материал FOREIGN KEY (id_материала)
        REFERENCES Материал(id_материала),
    CONSTRAINT UQ_Спец UNIQUE (id_продукции, id_материала)
);

/* ---------------------------------------------------------------------
   Заказы покупателей
--------------------------------------------------------------------- */
CREATE TABLE Заказ (
    id_заказа     INT IDENTITY(1,1) PRIMARY KEY,
    номер         NVARCHAR(20) NOT NULL,
    дата          DATE NOT NULL,
    id_покупателя NVARCHAR(9) NOT NULL,
    id_исполнителя NVARCHAR(9) NOT NULL,
    CONSTRAINT FK_Заказ_Покупатель FOREIGN KEY (id_покупателя)
        REFERENCES Заказчик(id_заказчика),
    CONSTRAINT FK_Заказ_Исполнитель FOREIGN KEY (id_исполнителя)
        REFERENCES Заказчик(id_заказчика)
);

CREATE TABLE Строка_заказа (
    id_строки_заказа INT IDENTITY(1,1) PRIMARY KEY,
    id_заказа        INT NOT NULL,
    id_продукции     INT NOT NULL,
    количество       DECIMAL(10,2) NOT NULL,
    цена             DECIMAL(10,2) NOT NULL,
    CONSTRAINT FK_Строка_Заказ FOREIGN KEY (id_заказа)
        REFERENCES Заказ(id_заказа),
    CONSTRAINT FK_Строка_Продукция FOREIGN KEY (id_продукции)
        REFERENCES Продукция(id_продукции)
);

/* ---------------------------------------------------------------------
   Производство продукции и списанные материалы
--------------------------------------------------------------------- */
CREATE TABLE Производство (
    id_производства INT IDENTITY(1,1) PRIMARY KEY,
    номер           NVARCHAR(20) NOT NULL,
    дата            DATE NOT NULL,
    id_продукции    INT NOT NULL,
    количество      DECIMAL(10,2) NOT NULL,
    id_ед_изм       INT NOT NULL,
    CONSTRAINT FK_Произв_Продукция FOREIGN KEY (id_продукции)
        REFERENCES Продукция(id_продукции),
    CONSTRAINT FK_Произв_ЕдИзм FOREIGN KEY (id_ед_изм)
        REFERENCES Единица_измерения(id_ед_изм)
);

CREATE TABLE Состав_производства (
    id_состава_произв INT IDENTITY(1,1) PRIMARY KEY,
    id_производства   INT NOT NULL,
    id_материала      INT NOT NULL,
    количество        DECIMAL(10,4) NOT NULL,
    CONSTRAINT FK_СоставПр_Производство FOREIGN KEY (id_производства)
        REFERENCES Производство(id_производства),
    CONSTRAINT FK_СоставПр_Материал FOREIGN KEY (id_материала)
        REFERENCES Материал(id_материала)
);

/* ---------------------------------------------------------------------
   Таблица пользователей (для модуля 4)
--------------------------------------------------------------------- */
CREATE TABLE Пользователи (
    id_пользователя INT IDENTITY(1,1) PRIMARY KEY,
    логин           NVARCHAR(50) NOT NULL UNIQUE,
    пароль          NVARCHAR(50) NOT NULL,
    роль            NVARCHAR(20) NOT NULL
        CONSTRAINT CK_Роль CHECK (роль IN (N'Администратор', N'Пользователь')),
    заблокирован    BIT NOT NULL DEFAULT 0,
    число_попыток   INT NOT NULL DEFAULT 0
);
GO

/* =====================================================================
   Заполнение справочников
   ===================================================================== */
INSERT INTO Единица_измерения (наименование) VALUES (N'шт'), (N'кг');
GO

-- Материалы с ценами из файла "Цены.xlsx"
DECLARE @шт INT = (SELECT id_ед_изм FROM Единица_измерения WHERE наименование = N'шт');
DECLARE @кг INT = (SELECT id_ед_изм FROM Единица_измерения WHERE наименование = N'кг');

INSERT INTO Материал (наименование, цена, id_ед_изм) VALUES
    (N'Изюм',                   150, @кг),
    (N'Масло сливочное',        124, @кг),
    (N'Молоко нормализованное',  34, @кг),
    (N'Мука',                   220, @кг),
    (N'Сода',                    60, @шт),
    (N'Яйца',                    80, @шт);

-- Продукция с ценами из файла "Цены.xlsx"
INSERT INTO Продукция (наименование, цена, id_ед_изм) VALUES
    (N'Булочка с изюмом', 35, @шт),
    (N'Хлеб белый 1 кг.', 42, @шт),
    (N'Хлеб ржаной 800г.', 47, @шт);
GO

/* ---------------------------------------------------------------------
   Спецификация "Булочка с изюмом" (по документам заказчика)
--------------------------------------------------------------------- */
DECLARE @булочка INT = (SELECT id_продукции FROM Продукция WHERE наименование = N'Булочка с изюмом');

INSERT INTO Спецификация (id_продукции, id_материала, норма_расхода)
SELECT @булочка, id_материала, n.норма
FROM (VALUES
        (N'Изюм',                   0.02),
        (N'Масло сливочное',        0.02),
        (N'Молоко нормализованное', 0.15),
        (N'Мука',                   0.10),
        (N'Сода',                   0.005),
        (N'Яйца',                   0.25)
     ) AS n(материал, норма)
JOIN Материал m ON m.наименование = n.материал;
GO

/* =====================================================================
   Импорт заказчиков из файла "Заказчики.json"
   ВАЖНО: укажите фактический путь к файлу на сервере.
   ===================================================================== */
DECLARE @json NVARCHAR(MAX);

SELECT @json = BulkColumn
FROM OPENROWSET (BULK N'C:\DEMOEXAM\Заказчики.json', SINGLE_CLOB) AS j;

INSERT INTO Заказчик (id_заказчика, наименование, ИНН, адрес, телефон,
                      признак_продавец, признак_покупатель)
SELECT id, name,
       NULLIF(inn, N''),
       addres, phone, salesman, buyer
FROM OPENJSON(@json)
WITH (
    id       NVARCHAR(9)   N'$.id',
    name     NVARCHAR(150) N'$.name',
    inn      NVARCHAR(12)  N'$.inn',
    addres   NVARCHAR(200) N'$.addres',
    phone    NVARCHAR(20)  N'$.phone',
    salesman BIT           N'$.salesman',
    buyer    BIT           N'$.buyer'
);
GO

/* ---------------------------------------------------------------------
   Демонстрационный заказ (покупатель и исполнитель берутся из
   импортированных заказчиков)
--------------------------------------------------------------------- */
DECLARE @покупатель NVARCHAR(9) = N'000000003';   -- ООО "Ромашка", buyer = true
DECLARE @исполнитель NVARCHAR(9) = N'000000001';  -- ООО "Поставка", salesman = true

INSERT INTO Заказ (номер, дата, id_покупателя, id_исполнителя)
VALUES (N'3', '2025-06-07', @покупатель, @исполнитель);

DECLARE @заказ INT = SCOPE_IDENTITY();
DECLARE @булочка2 INT = (SELECT id_продукции FROM Продукция WHERE наименование = N'Булочка с изюмом');

INSERT INTO Строка_заказа (id_заказа, id_продукции, количество, цена)
VALUES (@заказ, @булочка2, 100, 35);
GO

/* ---------------------------------------------------------------------
   Учётные записи для входа в приложение (модуль 4)
--------------------------------------------------------------------- */
INSERT INTO Пользователи (логин, пароль, роль) VALUES
    (N'admin', N'admin', N'Администратор'),
    (N'user',  N'user',  N'Пользователь');
GO
