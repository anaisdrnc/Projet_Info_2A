DROP TABLE IF EXISTS order_products CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS administrator CASCADE;
DROP TABLE IF EXISTS driver CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-----------------------
-- USERS
-----------------------
CREATE TABLE users (
    id_user        SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    user_name      VARCHAR(30) UNIQUE NOT NULL,
    password       VARCHAR(256) NOT NULL,
    email          VARCHAR(100) UNIQUE NOT NULL
);

-----------------------
-- CUSTOMER
----------------------- 
CREATE TABLE customer (
    id_customer    SERIAL PRIMARY KEY,
    id_user        INT NOT NULL,
    address        VARCHAR(100),
    city           VARCHAR(50),
    postal_code    VARCHAR(5) CHECK (char_length(postal_code) = 5),
    CONSTRAINT fk_customer_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

-----------------------
-- ADDRESS
-----------------------
CREATE TABLE address (
    id_address   SERIAL PRIMARY KEY,
    address      VARCHAR(100),
    city         VARCHAR(50),
    postal_code  VARCHAR(5) CHECK (char_length(postal_code) = 5)
);

-----------------------
-- DRIVER
-----------------------
CREATE TABLE driver (
    id_driver          SERIAL PRIMARY KEY,
    id_user            INT NOT NULL,
    mean_of_transport  VARCHAR(50) NOT NULL,
    CONSTRAINT fk_driver_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

-----------------------
-- ADMINISTRATOR
-----------------------
CREATE TABLE administrator (
    id_administrator   SERIAL PRIMARY KEY,
    id_user            INT NOT NULL,
    CONSTRAINT fk_admin_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

-----------------------
-- PRODUCT
-----------------------
CREATE TABLE product (
    id_product       SERIAL PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    price            DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    production_cost  DECIMAL(10,2) NOT NULL CHECK (production_cost >= 0),
    product_type             VARCHAR(20) NOT NULL, 
    description      TEXT,
    stock            INT NOT NULL CHECK (stock >= 0)
);

-----------------------
-- ORDERS
-----------------------
CREATE TABLE orders (
    id_order            SERIAL PRIMARY KEY,
    id_customer         INT NOT NULL,
    id_driver           INT NOT NULL,
    id_address          INT NOT NULL,
    date                TIMESTAMP NOT NULL DEFAULT NOW(),
    status              VARCHAR(30) NOT NULL,
    nb_items            INT CHECK (nb_items >= 0),
    total_amount        DECIMAL(10,2) CHECK (total_amount >= 0),
    payment_method      VARCHAR(50),
    CONSTRAINT fk_order_customer FOREIGN KEY (id_customer) REFERENCES customer(id_customer) ON DELETE CASCADE,
    CONSTRAINT fk_order_driver FOREIGN KEY (id_driver) REFERENCES driver(id_driver) ON DELETE CASCADE,
    CONSTRAINT fk_order_address FOREIGN KEY (id_address) REFERENCES address(id_address) ON DELETE CASCADE
);

-----------------------
-- ORDER_PRODUCTS
-----------------------
CREATE TABLE order_products (
    id_order    INT NOT NULL,
    id_product  INT NOT NULL,
    quantity    INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (id_order, id_product),
    CONSTRAINT fk_op_order FOREIGN KEY (id_order) REFERENCES orders(id_order) ON DELETE CASCADE,
    CONSTRAINT fk_op_product FOREIGN KEY (id_product) REFERENCES product(id_product) ON DELETE CASCADE
);


