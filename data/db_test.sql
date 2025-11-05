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
CREATE TABLE test.users (
    id_user        SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    user_name      VARCHAR(100) UNIQUE NOT NULL,
    password       VARCHAR(256) NOT NULL,
    email          VARCHAR(100) UNIQUE NOT NULL,
    salt           VARCHAR(256) NOT NULL
);

-----------------------
-- CUSTOMER
----------------------- 
CREATE TABLE test.customer (
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
CREATE TABLE test.address (
    id_address   SERIAL PRIMARY KEY,
    address      VARCHAR(100),
    city         VARCHAR(50),
    postal_code  VARCHAR(5) CHECK (char_length(postal_code) = 5)
);

-----------------------
-- DRIVER
-----------------------
CREATE TABLE test.driver (
    id_driver          SERIAL PRIMARY KEY,
    id_user            INT NOT NULL,
    mean_of_transport  VARCHAR(50) NOT NULL,
    CONSTRAINT fk_driver_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

-----------------------
-- ADMINISTRATOR
-----------------------
CREATE TABLE test.administrator (
    id_administrator   SERIAL PRIMARY KEY,
    id_user            INT NOT NULL,
    CONSTRAINT fk_admin_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

-----------------------
-- PRODUCT
-----------------------
CREATE TABLE test.product (
    id_product       SERIAL PRIMARY KEY,
    name             VARCHAR(100) UNIQUE NOT NULL,
    price            DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    production_cost  DECIMAL(10,2) NOT NULL CHECK (production_cost >= 0),
    product_type             VARCHAR(20) NOT NULL, 
    description      TEXT,
    stock            INT NOT NULL CHECK (stock >= 0)
);

-----------------------
-- ORDERS
-----------------------
CREATE TABLE test.orders (
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
CREATE TABLE test.order_products (
    id_order    INT NOT NULL,
    id_product  INT NOT NULL,
    quantity    INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (id_order, id_product),
    CONSTRAINT fk_op_order FOREIGN KEY (id_order) REFERENCES orders(id_order) ON DELETE CASCADE,
    CONSTRAINT fk_op_product FOREIGN KEY (id_product) REFERENCES product(id_product) ON DELETE CASCADE
);

-----------------------
-- USERS
-----------------------
INSERT INTO users (id_user, first_name, last_name, user_name, password, email) VALUES
(999, 'Admin', 'System', 'admin', '69371091eb0f9aec7e61b7421cf3044529167e979cd975201909eb8ae33887ba', 'admin@project.com'),
(998, 'Alice', 'Martin', 'AliceM', 'eb03c057f2207cc124b4cda1e0959b72d220a33916b5e638705e3d6525a01dbf', 'alice@test.com'), 
(997, 'Bob', 'Durand', 'BobD', '0cfae64be65ba050f9ec04146962114f3a550bf7b7ebad28179e543b47068132', 'bob@test.com'), 
(996, 'Charlie', 'Dupont','ChaCha', 'fef0cbb48e4c82a6bdcd62b27bc4c73fef56ead5bc148cc210e5b87148c12009', 'charlie@test.com'),
(995, 'Diane', 'Lemoine', 'DiDi','cc731e1c53078b48cc777353778b20df1fa479cf1aa991d5509ebaaffadba883', 'diane@test.com');


-----------------------
-- CUSTOMER
-----------------------
INSERT INTO customer (id_customer, id_user, address, city, postal_code) VALUES
(999, 998, '10 Maple Street', 'Rennes', '35000'),
(998, 997, '22 Oak Avenue', 'Rennes', '35000');

-----------------------
-- ADDRESS
-----------------------
INSERT INTO address (id_address, address, city, postal_code) VALUES
(999, '10 Maple Street', 'Rennes', '35000'),
(998, '22 Oak Avenue', 'Rennes', '35000');

-----------------------
-- DRIVER
-----------------------
INSERT INTO driver (id_driver, id_user, mean_of_transport) VALUES
(999, 996, 'Car'),
(998, 995, 'Bike');

-----------------------
-- ADMINISTRATOR
-----------------------
INSERT INTO administrator (id_administrator, id_user) VALUES
(999, 999);

-----------------------
-- PRODUCT
-----------------------
INSERT INTO product (id_product, name, price, production_cost, description, product_type, stock) VALUES
(999, 'Test Panini', 3.00, 2.00, 'Simple panini for test', 'lunch', 10),
(998, 'Test Cake', 1.00, 0.50, 'Chocolate test cake', 'dessert', 5),
(997, 'Test Drink', 1.50, 0.50, 'Small soda can', 'drink', 20);

-----------------------
-- ORDERS
-----------------------
INSERT INTO orders (id_order, id_customer, id_driver, id_address, date, status, nb_items, total_amount, payment_method) VALUES
(999, 999, 999, 999, NOW(),'Preparing', 2, 4.50, 'Credit Card'),
(998, 998, 998, 998, NOW(), 'Delivered', 1, 3.00, 'Cash');

-----------------------
-- ORDER_PRODUCTS
-----------------------
INSERT INTO order_products (id_order, id_product, quantity) VALUES
(999, 999, 1),
(999, 998, 1),
(998, 997, 1);
