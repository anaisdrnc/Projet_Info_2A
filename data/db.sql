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
CREATE TABLE default_schema.users (
    id_user        SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    user_name      VARCHAR(100) UNIQUE NOT NULL,
    password       VARCHAR(256) NOT NULL,
    email          VARCHAR(100) UNIQUE NOT NULL
);

-----------------------
-- CUSTOMER
----------------------- 
CREATE TABLE default_schema.customer (
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
CREATE TABLE default_schema.address (
    id_address   SERIAL PRIMARY KEY,
    address      VARCHAR(100),
    city         VARCHAR(50),
    postal_code  VARCHAR(5) CHECK (char_length(postal_code) = 5)
);

-----------------------
-- DRIVER
-----------------------
CREATE TABLE default_schema.driver (
    id_driver          SERIAL PRIMARY KEY,
    id_user            INT NOT NULL,
    mean_of_transport  VARCHAR(50) NOT NULL,
    CONSTRAINT fk_driver_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

-----------------------
-- ADMINISTRATOR
-----------------------
CREATE TABLE default_schema.administrator (
    id_administrator   SERIAL PRIMARY KEY,
    id_user            INT NOT NULL,
    CONSTRAINT fk_admin_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

-----------------------
-- PRODUCT
-----------------------
CREATE TABLE default_schema.product (
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
CREATE TABLE default_schema.orders (
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
CREATE TABLE default_schema.order_products (
    id_order    INT NOT NULL,
    id_product  INT NOT NULL,
    quantity    INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (id_order, id_product),
    CONSTRAINT fk_op_order FOREIGN KEY (id_order) REFERENCES orders(id_order) ON DELETE CASCADE,
    CONSTRAINT fk_op_product FOREIGN KEY (id_product) REFERENCES product(id_product) ON DELETE CASCADE
);

-----------------------
-- INSERT INTO USERS
-----------------------
INSERT INTO users (first_name, last_name, user_name, password, email) VALUES
('Admin', 'System', 'admin', '69371091eb0f9aec7e61b7421cf3044529167e979cd975201909eb8ae33887ba', 'admin@project.com'),
('Neo', 'Gandhaye', 'SecretNeo', '671ac9d528b52b5d47f8ab43c74d4584fba7af774cd8f376d96bf6c45b01b796', 'secretneo@project.com'),
('Emma', 'Boisse', 'EmmaMache', '8d3a5fcc03ea32df25e905dc47b27c4d8a5fabf9f77bbec1a305a59af5ab9143', 'emmamache@project.com'),
('Emma', 'Glorieux', 'EmmaDriver', 'f11b5649b0e3b97afae7b6db66b48f66407096f4771d599159ea7d0d7cd1d8de', 'emmadriver@project.com'),
('JF', 'Lapitre', 'PresidentEnsai', '118adf271202feab0f44fb1a53285c72ab1857e8d49ca2c930cfee09da4555bf', 'jf@project.com');

-----------------------
-- INSERT INTO CUSTOMER
-----------------------
INSERT INTO customer (id_user, address, city, postal_code) VALUES
(2, '12 Yvonne Jean-Haffen Street', 'Rennes', '35000'),
(3, '1 Rohan Street', 'Rennes', '35000');

-----------------------
-- INSERT INTO ADDRESS
-----------------------
INSERT INTO address (address, city, postal_code) VALUES
('12 Yvonne Jean-Haffen Street', 'Rennes', '35000'),
('1 Rohan Street', 'Rennes', '35000');

-----------------------
-- INSERT INTO DRIVER
-----------------------
INSERT INTO driver (id_user, mean_of_transport) VALUES
(4, 'Car'),
(5, 'Car');

-----------------------
-- INSERT INTO ADMINISTRATOR
-----------------------
INSERT INTO administrator (id_user) VALUES
(1);

-----------------------
-- INSERT INTO PRODUCT
-----------------------
INSERT INTO product (name, price, production_cost, description, product_type, stock) VALUES
-- Lunch
('Italian Panini', 3.00, 2.00, 'Chicken, fresh tomatoes, mozzarella', 'lunch', 20),
('Indian Panini', 3.00, 2.00, 'Chicken, curry, mozzarella', 'lunch', 20),
('Goat Cheese & Honey Panini', 3.00, 2.00, 'Onions, cream, goat cheese, honey', 'lunch', 20),
('Pesto Panini', 3.00, 2.00, 'Pesto, mozzarella, fresh or sun-dried tomatoes', 'lunch', 20),
('Classic Kebab', 3.00, 2.00, 'Chicken, sauce of choice, endive, lettuce, onions', 'lunch', 20),
('Veggie Kebab', 3.00, 2.00, 'Falafels, rösti, herb sauce, white cabbage, lettuce, tomatoes', 'lunch', 20),
('Classic Fajitas', 3.00, 2.00, 'Chicken, onion, tomatoes, guacamole, grated cheese, lemon', 'lunch', 20),
('Veggie Fajitas', 3.00, 2.00, 'Lettuce, zucchini, carrots, mozzarella, red beans', 'lunch', 20),
('Ham Croque', 3.00, 2.00, 'Sliced bread, ham, cheese', 'lunch', 20),
('Veggie Croque', 3.00, 2.00, 'Sliced bread, tomato sauce, mushrooms, bell peppers', 'lunch', 20),
('Classic Hot Dog', 3.00, 2.00, 'Sausage, mustard, grated cheese, onions, sauce of choice', 'lunch', 20),
('Veggie Hot Dog', 3.00, 2.00, 'Carrot, olive oil, arugula, sauce of choice', 'lunch', 20),
('Classic Burger', 3.00, 2.00, 'Beef patty, mustard, tomatoes, emmental or cheddar, pickles', 'lunch', 20),
('Veggie Burger', 3.00, 2.00, 'Rösti, avocado, chickpeas, radish, sauce of choice', 'lunch', 20),
('Chicken Curry Rice', 3.00, 2.00, 'Chicken, rice, curry sauce, coconut milk', 'lunch', 20),
('Veggie Curry Rice', 3.00, 2.00, 'Tofu, rice, curry sauce, coconut milk', 'lunch', 20),
('Chicken Wrap', 3.00, 2.00, 'Chicken, guacamole, cheese, raw vegetables, salsa sauce', 'lunch', 20),
('Veggie Wrap', 3.00, 2.00, 'Mozza sticks, raw vegetables, salsa sauce', 'lunch', 20),

-- Dessert
('Chocolate Cake', 1.00, 0.50, 'Rich chocolate sponge cake', 'dessert', 15),
('Fruit Salad', 1.00, 0.50, 'Mix of fresh seasonal fruits', 'dessert', 15),
('Ice Cream Sundae', 1.00, 0.50, 'Vanilla ice cream with chocolate syrup', 'dessert', 15),

-- Drinks
('Coca Cola', 1.50, 0.50, 'Classic soda 33cl', 'drink', 30),
('Orange Juice', 2.00, 0.80, 'Freshly squeezed orange juice', 'drink', 25),
('Water Bottle', 1.00, 0.30, 'Still mineral water 50cl', 'drink', 50);


-----------------------
-- INSERT INTO ORDERS
-----------------------
INSERT INTO orders (id_customer, id_driver, id_address, date, status, nb_items, total_amount, payment_method) VALUES
(1, 1, 1, NOW(),'Preparing', 2, 6.00, 'Credit Card'),
(2, 2, 2, NOW(),'Delivered', 1, 3.00, 'Cash');

-----------------------
-- INSERT INTO ORDER_PRODUCTS
-----------------------
INSERT INTO order_products (id_order, id_product, quantity) VALUES
(1, 1, 1),  -- 1 Italian Panini in order 1
(1, 13, 1),  -- 1 Classic Burger in order 1
(2, 17, 1);  -- 1 Chicken Wrap in order 2



