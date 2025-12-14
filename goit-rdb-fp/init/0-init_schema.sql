DROP TABLE IF EXISTS disease_data_raw;

CREATE TABLE disease_data_raw (
    entity                  text,
    code                    text,
    year                    integer,
    number_yaws             numeric,
    polio_cases             numeric,
    cases_guinea_worm       numeric,
    number_rabies           numeric,
    number_malaria          numeric,
    number_hiv              numeric,
    number_tuberculosis     numeric,
    number_smallpox         numeric,
    number_cholera_cases    numeric
);

DROP TABLE IF EXISTS disease_cases;
DROP TABLE IF EXISTS diseases;
DROP TABLE IF EXISTS countries;

CREATE TABLE countries (
    country_id      bigserial PRIMARY KEY,
    entity          text NOT NULL,
    code            text NOT NULL,
    CONSTRAINT uq_countries_code UNIQUE (code)
);

CREATE TABLE diseases (
    disease_id      bigserial PRIMARY KEY,
    disease_key     text NOT NULL,
    disease_name    text NOT NULL,
    CONSTRAINT uq_diseases_key UNIQUE (disease_key)
);

CREATE TABLE disease_cases (
    country_id      bigint NOT NULL REFERENCES countries(country_id) ON DELETE RESTRICT,
    year            integer NOT NULL,
    disease_id      bigint NOT NULL REFERENCES diseases(disease_id) ON DELETE RESTRICT,
    cases           numeric NULL,
    PRIMARY KEY (country_id, year, disease_id),
    CONSTRAINT chk_year_reasonable CHECK (year BETWEEN 1800 AND 2200),
    CONSTRAINT chk_cases_non_negative CHECK (cases IS NULL OR cases >= 0)
);

CREATE INDEX IF NOT EXISTS idx_disease_cases_country_year ON disease_cases (country_id, year);
CREATE INDEX IF NOT EXISTS idx_disease_cases_disease_year ON disease_cases (disease_id, year);

