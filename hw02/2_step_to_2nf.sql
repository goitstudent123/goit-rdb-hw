DROP TABLE IF EXISTS orders_2nf CASCADE;
DROP TABLE IF EXISTS order_items_2nf;

CREATE TABLE orders_2nf (
    order_id       INTEGER      NOT NULL,
    client_name    TEXT         NOT NULL,
    client_address TEXT         NOT NULL,
    order_date     DATE         NOT NULL,
    CONSTRAINT pk_orders_2nf PRIMARY KEY (order_id)
);

CREATE TABLE order_items_2nf (
    order_id     INTEGER NOT NULL,
    product_name TEXT    NOT NULL,
    quantity     INTEGER NOT NULL,
    CONSTRAINT pk_order_items_2nf PRIMARY KEY (order_id, product_name),
    CONSTRAINT fk_order_items_2nf_order
        FOREIGN KEY (order_id) REFERENCES orders_2nf(order_id)
);

INSERT INTO orders_2nf (order_id, client_name, client_address, order_date)
SELECT DISTINCT
    order_id,
    client_name,
    client_address,
    order_date
FROM orders_1nf;

INSERT INTO order_items_2nf (order_id, product_name, quantity)
SELECT
    order_id,
    product_name,
    quantity
FROM orders_1nf;

DROP TABLE IF EXISTS orders_1nf;
