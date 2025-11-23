DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS shippers;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;

CREATE TABLE categories (
    id          integer PRIMARY KEY,
    name        text NOT NULL,
    description text
);

CREATE TABLE customers (
    id           integer PRIMARY KEY,
    name         text NOT NULL,
    contact      text,
    address      text,
    city         text,
    postal_code  text,
    country      text
);

CREATE TABLE employees (
    employee_id  integer PRIMARY KEY,
    last_name    text NOT NULL,
    first_name   text NOT NULL,
    birthdate    date,
    photo        text,
    notes        text
);

CREATE TABLE shippers (
    id     integer PRIMARY KEY,
    name   text NOT NULL,
    phone  text
);

CREATE TABLE suppliers (
    id           integer PRIMARY KEY,
    name         text NOT NULL,
    contact      text,
    address      text,
    city         text,
    postal_code  text,
    country      text,
    phone        text
);

-- Products

CREATE TABLE products (
    id             integer PRIMARY KEY,
    name           text NOT NULL,
    supplier_id   integer NOT NULL,
    category_id   integer NOT NULL,
    unit           text,
    price          numeric(10,2) NOT NULL,

    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES categories (id)
);

-- Orders

CREATE TABLE orders (
    id            integer PRIMARY KEY,
    customer_id  integer NOT NULL,
    employee_id  integer NOT NULL,
    date          date NOT NULL,
    shipper_id   integer NOT NULL,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers (id),
    CONSTRAINT fk_orders_employee
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
    CONSTRAINT fk_orders_shipper
        FOREIGN KEY (shipper_id) REFERENCES shippers (id)
);

-- Order line items

CREATE TABLE order_details (
    id           integer PRIMARY KEY,
    order_id    integer NOT NULL,
    product_id  integer NOT NULL,
    quantity     integer NOT NULL,

    CONSTRAINT fk_order_details_order
        FOREIGN KEY (order_id) REFERENCES orders (id),
    CONSTRAINT fk_order_details_product
        FOREIGN KEY (product_id) REFERENCES products (id),

    -- Each product appears at most once per order
    CONSTRAINT uq_order_details_order_product
        UNIQUE (order_id, product_id)
);

-- Helpful indexes (read-optimized)

CREATE INDEX idx_customers_country_city
    ON customers (country, city);

CREATE INDEX idx_employees_last_name
    ON employees (last_name);

CREATE INDEX idx_products_category_id
    ON products (category_id);

CREATE INDEX idx_products_supplier_id
    ON products (supplier_id);

CREATE INDEX idx_orders_date
    ON orders (date);

CREATE INDEX idx_orders_customer_id
    ON orders (customer_id);

CREATE INDEX idx_orders_employee_id
    ON orders (employee_id);

CREATE INDEX idx_order_details_order_id
    ON order_details (order_id);

CREATE INDEX idx_order_details_product_id
    ON order_details (product_id);
