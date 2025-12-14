INSERT INTO countries (entity, code)
SELECT MIN(entity) AS entity,
       code
FROM disease_data_raw
WHERE code IS NOT NULL
  AND code <> ''
GROUP BY code;

INSERT INTO diseases (disease_key, disease_name)
VALUES ('yaws', 'Yaws'),
       ('polio', 'Polio'),
       ('guinea_worm', 'Guinea worm disease'),
       ('rabies', 'Rabies'),
       ('malaria', 'Malaria'),
       ('hiv', 'HIV'),
       ('tuberculosis', 'Tuberculosis'),
       ('smallpox', 'Smallpox'),
       ('cholera', 'Cholera');

INSERT INTO disease_cases (country_id, year, disease_id, cases)
SELECT c.country_id,
       r.year,
       d.disease_id,
       v.cases
FROM disease_data_raw r
         JOIN countries c
              ON c.code = r.code
         CROSS JOIN LATERAL (
    VALUES ('yaws', r.number_yaws),
           ('polio', r.polio_cases),
           ('guinea_worm', r.cases_guinea_worm),
           ('rabies', r.number_rabies),
           ('malaria', r.number_malaria),
           ('hiv', r.number_hiv),
           ('tuberculosis', r.number_tuberculosis),
           ('smallpox', r.number_smallpox),
           ('cholera', r.number_cholera_cases)
        ) AS v(disease_key, cases)
         JOIN diseases d
              ON d.disease_key = v.disease_key
WHERE r.year IS NOT NULL
  AND r.code IS NOT NULL
  AND r.code <> ''
  AND v.cases IS NOT NULL;
