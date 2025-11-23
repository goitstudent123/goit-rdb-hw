ALTER TABLE clients_3nf  RENAME TO clients;
ALTER TABLE products_3nf RENAME TO products;
ALTER TABLE orders_3nf   RENAME TO orders;
ALTER TABLE order_items_3nf RENAME TO order_items;

ALTER TABLE clients RENAME COLUMN client_id      TO id;
ALTER TABLE clients RENAME COLUMN client_name    TO name;
ALTER TABLE clients RENAME COLUMN client_address TO address;

ALTER TABLE products RENAME COLUMN product_id   TO id;
ALTER TABLE products RENAME COLUMN product_name TO name;

ALTER TABLE orders RENAME COLUMN order_id  TO id;
ALTER TABLE orders RENAME COLUMN client_id TO client_ref;

ALTER TABLE order_items RENAME COLUMN order_id   TO order_ref;
ALTER TABLE order_items RENAME COLUMN product_id TO product_ref;
