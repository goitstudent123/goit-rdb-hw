-- Виконайте запит SELECT COUNT(*) FROM infectious_cases , щоб ментор міг зрозуміти, скільки записів ви завантажили у базу даних із файла.
select count(*) from disease_data_raw;
-- 10521

select count(*) from disease_cases
-- 43029

-- 3. Проаналізуйте дані:
-- Для кожної унікальної комбінації Entity та Code або їх id порахуйте середнє, мінімальне, максимальне значення та суму для атрибута Number_rabies.
-- 💡 Врахуйте, що атрибут Number_rabies може містити порожні значення ‘’ — вам попередньо необхідно їх відфільтрувати.
-- Результат відсортуйте за порахованим середнім значенням у порядку спадання.
-- Оберіть тільки 10 рядків для виведення на екран.

SELECT
    c.code,
    c.entity,
    MIN(dc.cases) AS min_cases,
    MAX(dc.cases) AS max_cases,
    AVG(dc.cases) AS avg_cases,
    SUM(dc.cases) AS sum_cases
FROM disease_cases dc
JOIN diseases d
  ON d.disease_id = dc.disease_id
JOIN countries c
  ON c.country_id = dc.country_id
WHERE d.disease_key = 'rabies'
GROUP BY c.country_id, c.code, c.entity
ORDER BY avg_cases DESC
LIMIT 10;

-- 4. Побудуйте колонку різниці в роках.
-- Для оригінальної або нормованої таблиці для колонки Year побудуйте з використанням вбудованих SQL-функцій:
-- атрибут, що створює дату першого січня відповідного року,
-- 💡 Наприклад, якщо атрибут містить значення ’1996’, то значення нового атрибута має бути ‘1996-01-01’.
-- атрибут, що дорівнює поточній даті,
-- атрибут, що дорівнює різниці в роках двох вищезгаданих колонок.
-- 💡 Перераховувати всі інші атрибути, такі як Number_malaria, не потрібно.
-- 👉🏼 Для пошуку необхідних вбудованих функцій вам може знадобитися матеріал до теми 7.

-- normalized
SELECT
    dc.year,
    make_date(dc.year, 1, 1)        AS year_start_date,
    current_date                    AS today,
    EXTRACT(YEAR FROM age(current_date, make_date(dc.year, 1, 1)))::int
                                     AS years_difference
FROM disease_cases dc;

-- original
SELECT
  r.year,
  make_date(r.year, 1, 1)         AS year_start_date,
  current_date                    AS today,
  EXTRACT(YEAR FROM age(current_date, make_date(r.year, 1, 1)))::int
                                  AS years_difference
FROM disease_data_raw r;

-- ============================================================
-- TASK 5
-- Function that:
--  - accepts a year
--  - builds date: YYYY-01-01
--  - returns difference in years vs current date
-- ============================================================

DROP FUNCTION IF EXISTS years_diff_from_now(integer);

CREATE FUNCTION years_diff_from_now(p_year integer)
RETURNS integer
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT EXTRACT(
               YEAR FROM age(current_date, make_date(p_year, 1, 1))
           )::integer;
$$;


SELECT years_diff_from_now(1996);
-- 29

SELECT
    year,
    years_diff_from_now(year) AS years_diff
FROM disease_data_raw
WHERE year IS NOT NULL;

