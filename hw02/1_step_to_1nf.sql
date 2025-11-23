DROP TABLE IF EXISTS orders_1nf;

CREATE TABLE orders_1nf (
    order_id       INTEGER      NOT NULL,
    product_name   TEXT         NOT NULL,
    quantity       INTEGER      NOT NULL,
    client_name    TEXT         NOT NULL,
    client_address TEXT         NOT NULL,
    order_date     DATE         NOT NULL,
    CONSTRAINT pk_orders_1nf PRIMARY KEY (order_id, product_name)
);

INSERT INTO orders_1nf (order_id, product_name, quantity, client_name, client_address, order_date)
SELECT
    o.order_id,
    trim(split_part(item_part, ':', 1)) AS product_name,
    trim(split_part(item_part, ':', 2))::INTEGER AS quantity,
    o.client_name,
    o.client_address,
    o.order_date
FROM orders AS o
CROSS JOIN LATERAL regexp_split_to_table(o.items, '\s*,\s*') AS item_part;

DROP TABLE IF EXISTS orders;
