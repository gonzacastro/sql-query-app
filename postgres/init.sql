-- =============================================================================
-- init.sql — crea la tabla sales y carga el CSV
-- Ejecutado automáticamente por PostgreSQL al primer arranque del container
-- =============================================================================

-- Tabla principal
CREATE TABLE IF NOT EXISTS sales (
    id            SERIAL PRIMARY KEY,
    date          DATE           NOT NULL,
    week_day      VARCHAR(10)    NOT NULL,
    hour          TIME           NOT NULL,
    ticket_number VARCHAR(30)    NOT NULL,
    waiter        INTEGER        NOT NULL,
    product_name  VARCHAR(100)   NOT NULL,
    quantity      NUMERIC(10, 2) NOT NULL,
    unitary_price NUMERIC(12, 2) NOT NULL,
    total         NUMERIC(12, 2) NOT NULL
);

-- Tabla staging: recibe el CSV tal cual (todo TEXT) para luego castear
-- Necesario porque la fecha viene en MM/DD/YYYY, no en el formato default de Postgres
CREATE TEMP TABLE sales_staging (
    date          TEXT,
    week_day      TEXT,
    hour          TEXT,
    ticket_number TEXT,
    waiter        TEXT,
    product_name  TEXT,
    quantity      TEXT,
    unitary_price TEXT,
    total         TEXT
);

-- Carga el CSV en staging
COPY sales_staging (date, week_day, hour, ticket_number, waiter, product_name, quantity, unitary_price, total)
FROM '/docker-entrypoint-initdb.d/data.csv'
WITH (FORMAT CSV, HEADER TRUE);

-- Inserta en la tabla real casteando cada columna al tipo correcto
INSERT INTO sales (date, week_day, hour, ticket_number, waiter, product_name, quantity, unitary_price, total)
SELECT
    TO_DATE(date, 'MM/DD/YYYY'),
    week_day,
    hour::TIME,
    ticket_number,
    waiter::INTEGER,
    product_name,
    quantity::NUMERIC,
    unitary_price::NUMERIC,
    total::NUMERIC
FROM sales_staging;

-- Índices para acelerar las queries más comunes
CREATE INDEX idx_sales_date         ON sales(date);
CREATE INDEX idx_sales_week_day     ON sales(week_day);
CREATE INDEX idx_sales_product_name ON sales(product_name);
