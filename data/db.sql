-----------------------
-- INSERT INTO USERS
-----------------------
INSERT INTO users (first_name, last_name, user_name, password, email) VALUES
('Admin', 'System', 'admin', '0000', 'admin@project.com'),
('Neo', 'Gandhaye', 'SecretNeo', '123abc', 'secretneo@project.com'),
('Emma', 'Boisse', 'EmmaMache', 'ensalade', 'emmamache@project.com'),
('Emma', 'Glorieux', 'EmmaDriver', 'aaabbb', 'emmadriver@project.com'),
('JF', 'Lapitre', 'PresidentEnsai', 'bde<ensalade', 'jf@project.com');

-----------------------
-- INSERT INTO CUSTOMER
-----------------------
INSERT INTO customer (id_user, address, city, postal_code) VALUES
(2, '12 Yvonne Jean-Haffen Street', 'Rennes', '35000'),
(3, '1 Rohan Street', 'Rennes', '35000');

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
-- INSERT INTO ORDERS
-----------------------
INSERT INTO orders (id_customer, id_driver, status, delivery_address, delivery_postal_code, nb_items, total_amount, payment_method) VALUES
(1, 1, 'Preparing', '12 Yvonne Jean-Haffen Street', '35000', 2, 6.00, 'Credit Card'),
(2, 2, 'Delivered', '1 Rohan Street', '44000', 1, 3.00, 'Cash');

-----------------------
-- INSERT INTO ORDER_PRODUCTS
-----------------------
INSERT INTO order_products (id_order, id_product, quantity) VALUES
(1, 1, 1),  -- 1 Italian Panini in order 1
(1, 13, 1),  -- 1 Classic Burger in order 1
(2, 17, 1);  -- 1 Chicken Wrap in order 2

-----------------------
-- INSERT INTO PRODUCT
-----------------------
INSERT INTO product (name, price, description, stock) VALUES
('Italian Panini', 3.00, 'Chicken, fresh tomatoes, mozzarella', 20),
('Indian Panini', 3.00, 'Chicken, curry, mozzarella', 20),
('Goat Cheese & Honey Panini', 3.00, 'Onions, cream, goat cheese, honey', 20),
('Pesto Panini', 3.00, 'Pesto, mozzarella, fresh or sun-dried tomatoes', 20),
('Classic Kebab', 3.00, 'Chicken, sauce of choice, endive, lettuce, onions', 20),
('Veggie Kebab', 3.00, 'Falafels, rösti, herb sauce, white cabbage, lettuce, tomatoes', 20),
('Classic Fajitas', 3.00, 'Chicken, onion, tomatoes, guacamole, grated cheese, lemon', 20),
('Veggie Fajitas', 3.00, 'Lettuce, zucchini, carrots, mozzarella, red beans', 20),
('Ham Croque', 3.00, 'Sliced bread, ham, cheese', 20),
('Veggie Croque', 3.00, 'Sliced bread, tomato sauce, mushrooms, bell peppers', 20),
('Classic Hot Dog', 3.00, 'Sausage, mustard, grated cheese, onions, sauce of choice', 20),
('Veggie Hot Dog', 3.00, 'Carrot, olive oil, arugula, sauce of choice', 20),
('Classic Burger', 3.00, 'Beef patty, mustard, tomatoes, emmental or cheddar, pickles', 20),
('Veggie Burger', 3.00, 'Rösti, avocado, chickpeas, radish, sauce of choice', 20),
('Chicken Curry Rice', 3.00, 'Chicken, rice, curry sauce, coconut milk', 20),
('Veggie Curry Rice', 3.00, 'Tofu, rice, curry sauce, coconut milk', 20),
('Chicken Wrap', 3.00, 'Chicken, guacamole, cheese, raw vegetables, salsa sauce', 20),
('Veggie Wrap', 3.00, 'Mozza sticks, raw vegetables, salsa sauce', 20);
