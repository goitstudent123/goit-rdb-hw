DROP TABLE IF EXISTS order_items_3nf CASCADE;
DROP TABLE IF EXISTS orders_3nf CASCADE;
DROP TABLE IF EXISTS clients_3nf CASCADE;
DROP TABLE IF EXISTS products_3nf CASCADE;

CREATE TABLE clients_3nf (
    client_id      SERIAL       PRIMARY KEY,
    client_name    TEXT         NOT NULL UNIQUE,
    client_address TEXT         NOT NULL
);

CREATE TABLE products_3nf (
    product_id   SERIAL PRIMARY KEY,
    product_name TEXT  NOT NULL UNIQUE
);

CREATE TABLE orders_3nf (
    order_id   INTEGER NOT NULL,
    client_id  INTEGER NOT NULL,
    order_date DATE    NOT NULL,
    CONSTRAINT pk_orders_3nf PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_3nf_client
        FOREIGN KEY (client_id) REFERENCES clients_3nf(client_id)
);

CREATE TABLE order_items_3nf (
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL,
    CONSTRAINT pk_order_items_3nf PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_order_items_3nf_order
        FOREIGN KEY (order_id) REFERENCES orders_3nf(order_id),
    CONSTRAINT fk_order_items_3nf_product
        FOREIGN KEY (product_id) REFERENCES products_3nf(product_id)
);

INSERT INTO clients_3nf (client_name, client_address)
SELECT DISTINCT
    client_name,
    client_address
FROM orders_2nf;

INSERT INTO products_3nf (product_name)
SELECT DISTINCT
    product_name
FROM order_items_2nf;

INSERT INTO orders_3nf (order_id, client_id, order_date)
SELECT
    o.order_id,
    c.client_id,
    o.order_date
FROM orders_2nf AS o
JOIN clients_3nf AS c
  ON c.client_name = o.client_name;

INSERT INTO order_items_3nf (order_id, product_id, quantity)
SELECT
    oi.order_id,
    p.product_id,
    oi.quantity
FROM order_items_2nf AS oi
JOIN products_3nf AS p
  ON p.product_name = oi.product_name;

DROP TABLE IF EXISTS order_items_2nf;
DROP TABLE IF EXISTS orders_2nf;
