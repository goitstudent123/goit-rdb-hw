-- 1. Напишіть SQL-запит, який для таблиці orders з атрибута date витягує рік, місяць і число. Виведіть на екран їх у три окремі атрибути поряд з атрибутом id та оригінальним атрибутом date (всього вийде 5 атрибутів).
SELECT
    o.id,
    o."date",
    EXTRACT(YEAR  FROM o."date")::int  AS year,
    EXTRACT(MONTH FROM o."date")::int  AS month,
    EXTRACT(DAY   FROM o."date")::int  AS day
FROM orders o;

-- 2. Напишіть SQL-запит, який для таблиці orders до атрибута date додає один день. На екран виведіть атрибут id, оригінальний атрибут date та результат додавання.
SELECT
    o.id,
    o."date",
    o."date" + INTERVAL '1 day' AS date_plus_1_day
FROM orders o;

-- 3. Напишіть SQL-запит, який для таблиці orders для атрибута date відображає кількість секунд з початку відліку (показує його значення timestamp). Для цього потрібно знайти та застосувати необхідну функцію. На екран виведіть атрибут id, оригінальний атрибут date та результат роботи функції.
SELECT
    o.id,
    o."date",
    EXTRACT(EPOCH FROM o."date")::bigint AS epoch_seconds
FROM orders o;

-- 4. Напишіть SQL-запит, який рахує, скільки таблиця orders містить рядків з атрибутом date у межах між 1996-07-10 00:00:00 та 1996-10-08 00:00:00.
SELECT
    COUNT(*) AS cnt
FROM orders o
WHERE o."date" BETWEEN TIMESTAMP '1996-07-10 00:00:00'
                  AND TIMESTAMP '1996-10-08 00:00:00';

-- 5. Напишіть SQL-запит, який для таблиці orders виводить на екран атрибут id, атрибут date та JSON-об’єкт {"id": <атрибут id рядка>, "date": <атрибут date рядка>}. Для створення JSON-об’єкта використайте функцію.
SELECT
    o.id,
    o."date",
    json_build_object('id', o.id, 'date', o."date") AS obj
FROM orders o;
