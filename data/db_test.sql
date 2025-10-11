-----------------------
-- USERS
-----------------------
INSERT INTO users (id_user, first_name, last_name, user_name, password, email) VALUES
(999, 'Admin', 'System', 'admin', '0000', 'admin@project.com'),
(998, 'Alice', 'Martin', 'AliceM', 'alice', 'alice@test.com'),
(997, 'Bob', 'Durand', 'BobD', 'bob', 'bob@test.com'),
(996, 'Charlie', 'Dupont', 'CharlieD', 'charlie', 'charlie@test.com'),
(995, 'Diane', 'Lemoine', 'DianeL', 'diane', 'diane@test.com');

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
INSERT INTO product (id_product, name, price, production_cost, description, type, stock) VALUES
(999, 'Test Panini', 3.00, 2.00, 'Simple panini for test', 'lunch', 10),
(998, 'Test Cake', 1.00, 0.50, 'Chocolate test cake', 'dessert', 5),
(997, 'Test Drink', 1.50, 0.50, 'Small soda can', 'drink', 20);

-----------------------
-- ORDERS
-----------------------
INSERT INTO orders (id_order, id_customer, id_driver, id_address, status, nb_items, total_amount, payment_method) VALUES
(999, 999, 999, 999, 'Preparing', 2, 4.50, 'Credit Card'),
(998, 998, 998, 998, 'Delivered', 1, 3.00, 'Cash');

-----------------------
-- ORDER_PRODUCTS
-----------------------
INSERT INTO order_products (id_order, id_product, quantity) VALUES
(999, 999, 1),
(999, 998, 1),
(998, 997, 1);
