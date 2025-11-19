import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from DAO.DBConnector import DBConnector
from DAO.ProductDAO import ProductDAO
from Model.Address import Address
from Model.Order import Order
from utils.log_decorator import log


class OrderDAO:
    """Class providing access to the Order table of the database"""

    def __init__(self, db_connector=None):
        """Initialize OrderDAO with a DB connector."""
        self.db_connector = db_connector if db_connector is not None else DBConnector()
        self.productdao = ProductDAO(self.db_connector)

    @log
    def create_order(self, order: Order) -> Optional[int]:
        """Create a new order in the database.

        The order must reference an address that already exists in the database.

        Parameters
        ----------
        order : Order
            The Order object containing all necessary information to create the order.

        Returns
        -------
        int or None
            The ID of the newly created order if successful.
            None if the creation fails or an error occurs.
        """
        try:
            res_order = self.db_connector.sql_query(
                """
                INSERT INTO orders (id_customer, id_driver, id_address, date, status,
                                    total_amount, payment_method, nb_items)
                VALUES (%(id_customer)s, %(id_driver)s, %(id_address)s, %(date)s,
                        %(status)s, %(total_amount)s, %(payment_method)s, %(nb_items)s)
                RETURNING id_order;
                """,
                {
                    "id_customer": order.id_customer,
                    "id_driver": order.id_driver,
                    "id_address": order.id_address,
                    "date": order.date,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "payment_method": order.payment_method,
                    "nb_items": order.nb_items,
                },
                "one",
            )
            if res_order:
                return res_order["id_order"]
            return None
        except Exception as e:
            print(f"Error creating order: {e}")
            return None

    @log
    def add_product(self, order_id: int, product_id: int, quantity: int = 1, promotion: bool = False) -> bool:
        """Add a product to an existing order, update stock, and adjust order totals.

        This method:
            1) Decrements the product stock via ProductDAO.
            2) Inserts the product into the order_products table.
            3) Updates the order's nb_items and total_amount fields.
            4) Applies a 10% discount if promotion=True.

        Parameters
        ----------
        order_id : int
            The ID of the order to update.
        product_id : int
            The ID of the product to add.
        quantity : int, optional
            The quantity of the product to add (default is 1).
        promotion : bool, optional
            Whether to apply a 10% discount (default is False).

        Returns
        -------
        bool
            True if the product was successfully added and the order updated.
            False if stock is insufficient or an error occurs (stock is restored in that case).
        """
        try:
            success = self.productdao.decrement_stock(product_id, quantity)
            if not success:
                logging.warning(f"Stock insuffisant pour le produit {product_id}")
                return False

            self.db_connector.sql_query(
                """
                INSERT INTO order_products (id_order, id_product, quantity)
                VALUES (%s, %s, %s)
                """,
                [order_id, product_id, quantity],
                return_type=None,
            )

            product = self.db_connector.sql_query(
                "SELECT price FROM product WHERE id_product = %s",
                [product_id],
                "one",
            )
            if not product:
                raise Exception("Produit introuvable pour mise à jour commande")

            if promotion:
                total_add = float(product["price"]) * quantity * 0.9
            else:
                total_add = float(product["price"]) * quantity

            self.db_connector.sql_query(
                """
                UPDATE orders
                SET nb_items = COALESCE(nb_items, 0) + %s,
                    total_amount = COALESCE(total_amount, 0) + %s
                WHERE id_order = %s
                """,
                [quantity, total_add, order_id],
                return_type=None,
            )

            return True

        except Exception as e:
            logging.error(f"Erreur add_product: {e}")
            self.productdao.increment_stock(product_id, quantity)
            return False

    @log
    def remove_product(self, order_id: int, product_id: int, quantity: int = 1) -> bool:
        """Remove a product (or reduce its quantity) from an existing order and update stock and totals.

        This method:
            1) Checks the current quantity of the product in the order.
            2) Reduces the quantity or removes the product from order_products.
            3) Increments the product stock via ProductDAO.
            4) Updates the order's nb_items and total_amount fields accordingly.

        Parameters
        ----------
        order_id : int
            The ID of the order to update.
        product_id : int
            The ID of the product to remove.
        quantity : int, optional
            The quantity of the product to remove (default is 1).

        Returns
        -------
        bool
            True if the product was successfully removed or updated in the order.
            False if the product was not found in the order or an error occurs.
        """
        try:
            row = self.db_connector.sql_query(
                "SELECT quantity FROM order_products WHERE id_order = %s AND id_product = %s",
                [order_id, product_id],
                "one",
            )
            if not row:
                logging.warning(f"Produit {product_id} non trouvé dans la commande {order_id}")
                return False

            current_qty = row["quantity"]
            remove_qty = min(quantity, current_qty)

            if current_qty == remove_qty:
                self.db_connector.sql_query(
                    "DELETE FROM order_products WHERE id_order = %s AND id_product = %s",
                    [order_id, product_id],
                    return_type=None,
                )
            else:
                self.db_connector.sql_query(
                    "UPDATE order_products SET quantity = quantity - %s WHERE id_order = %s AND id_product = %s",
                    [remove_qty, order_id, product_id],
                    return_type=None,
                )

            self.productdao.increment_stock(product_id, remove_qty)

            product = self.db_connector.sql_query(
                "SELECT price FROM product WHERE id_product = %s",
                [product_id],
                "one",
            )
            total_reduce = float(product["price"]) * remove_qty

            self.db_connector.sql_query(
                """
                UPDATE orders
                SET nb_items = COALESCE(nb_items, 0) - %s,
                    total_amount = COALESCE(total_amount, 0) - %s
                WHERE id_order = %s
                """,
                [remove_qty, total_reduce, order_id],
                return_type=None,
            )

            return True

        except Exception as e:
            logging.error(f"Erreur remove_product: {e}")
            return False

    @log
    def cancel_order(self, id_order: int) -> bool:
        """Cancel an existing order by updating its status to 'Cancelled'.

        Parameters
        ----------
        id_order : int
            The ID of the order to cancel.

        Returns
        -------
        bool
            True if the order status was successfully updated.
            False if the order does not exist or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                "UPDATE orders SET status='Cancelled' WHERE id_order=%s RETURNING id_order",
                [id_order],
                return_type="one",
            )
            return res is not None
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return False

    @log
    def mark_as_delivered(self, id_order: int) -> bool:
        """Mark an existing order as delivered and update its delivery date.

        Parameters
        ----------
        id_order : int
            The ID of the order to mark as delivered.

        Returns
        -------
        bool
            True if the order status was successfully updated to 'Delivered' and the date set.
            False if the order does not exist or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                "UPDATE orders SET status='Delivered', date=%s WHERE id_order=%s RETURNING id_order",
                [datetime.now(), id_order],
                return_type="one",
            )
            return res is not None
        except Exception as e:
            print(f"Error marking order delivered: {e}")
            return False

    @log
    def mark_as_ready(self, id_order: int) -> bool:
        """Mark an existing order as ready for delivery and update its date.

        Parameters
        ----------
        id_order : int
            The ID of the order to mark as ready.

        Returns
        -------
        bool
            True if the order status was successfully updated to 'Ready' and the date set.
            False if the order does not exist or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                "UPDATE orders SET status='Ready', date=%s WHERE id_order=%s RETURNING id_order",
                [datetime.now(), id_order],
                return_type="one",
            )
            return res is not None
        except Exception as e:
            print(f"Error marking order ready: {e}")
            return False

    @log
    def mark_as_on_the_way(self, id_order: int) -> bool:
        """Mark an existing order as 'On the way' and update its date.

        Parameters
        ----------
        id_order : int
            The ID of the order to mark as on the way.

        Returns
        -------
        bool
            True if the order status was successfully updated to 'On the way' and the date set.
            False if the order does not exist or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                "UPDATE orders SET status='On the way', date=%s WHERE id_order=%s RETURNING id_order",
                [datetime.now(), id_order],
                return_type="one",
            )
            return res is not None
        except Exception as e:
            print(f"Error marking order on the way: {e}")
            return False

    @log
    def get_order_products(self, order_id: int) -> List[Dict[str, Any]]:
        """Retrieve all products associated with a specific order.

        Parameters
        ----------
        order_id : int
            The ID of the order whose products are to be retrieved.

        Returns
        -------
        List[Dict[str, Any]]
            A list of dictionaries, each containing product details (id_product, name, price, product_type)
            and the quantity for the specified order. Returns an empty list if no products are found
            or an error occurs."""
        try:
            rows = self.db_connector.sql_query(
                """
                SELECT p.id_product, p.name, p.price, p.product_type, op.quantity
                FROM order_products op
                JOIN product p ON p.id_product = op.id_product
                WHERE op.id_order = %s
                """,
                [order_id],
                "all",
            )
            return rows
        except Exception as e:
            print(f"Error fetching order products: {e}")
            return []

    @log
    def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve an order along with its associated address and products.

        Note
        ----
        This method does not modify the order in the database.

        Parameters
        ----------
        order_id : int
            The ID of the order to retrieve.

        Returns
        -------
        dict or None
            A dictionary with the following keys:
                - "order": Order object representing the order details.
                - "address": Address object associated with the order (or None if not found).
                - "products": List of dictionaries with product details and quantities.
            Returns None if the order does not exist or an error occurs.
        """
        try:
            raw_order = self.db_connector.sql_query("SELECT * FROM orders WHERE id_order = %s", [order_id], "one")
            if not raw_order:
                return None

            raw_address = self.db_connector.sql_query(
                "SELECT * FROM address WHERE id_address = %s",
                [raw_order["id_address"]],
                "one",
            )
            address = Address(**raw_address) if raw_address else None

            products = self.get_order_products(order_id)

            order_obj = Order(
                id_order=raw_order["id_order"],
                id_customer=raw_order["id_customer"],
                id_driver=raw_order["id_driver"],
                id_address=raw_order["id_address"],
                date=raw_order["date"],
                status=raw_order["status"],
                nb_items=raw_order["nb_items"],
                total_amount=float(raw_order["total_amount"]),
                payment_method=raw_order["payment_method"],
            )

            return {"order": order_obj, "address": address, "products": products}

        except Exception as e:
            print(f"Error fetching order: {e}")
            return None

    @log
    def list_all_orders(self) -> List[Dict[str, Any]]:
        """Retrieve all orders along with their associated addresses and products.

        Returns
        -------
        List[Dict[str, Any]]
            A list of dictionaries, each containing:
                - "order": Order object representing the order details.
                - "address": Address object associated with the order (or None if not found).
                - "products": List of dictionaries with product details and quantities.
            Returns an empty list if no orders are found or an error occurs.
        """
        try:
            raw_orders = self.db_connector.sql_query("SELECT * FROM orders", [], "all")
            result = []
            for o in raw_orders:
                order_data = self.get_by_id(o["id_order"])
                if order_data:
                    result.append(order_data)
            return result
        except Exception as e:
            print(f"Error listing all orders: {e}")
            return []

    @log
    def list_all_orders_ready(self) -> List[Dict[str, Any]]:
        """Retrieve all orders with status 'Ready', including their products and full address.

        Returns
        -------
        List[Dict[str, Any]]
            A list of dictionaries, each containing:
                - "order": Order object representing the order details.
                - "address": Address object associated with the order.
                - "products": List of dictionaries with product details and quantities.
            Returns an empty list if no ready orders are found or an error occurs.
        """
        try:
            raw_orders = self.db_connector.sql_query(
                """
                SELECT o.id_order, o.date, a.address, a.city, a.postal_code
                FROM orders o
                JOIN address a ON o.id_address = a.id_address
                WHERE o.status = 'Ready'
                ORDER BY o.date
                """,
                None,
                "all",
            )

            result = []
            for o in raw_orders:
                order_data = self.get_by_id(o["id_order"])
                if order_data:
                    result.append(order_data)
            return result
        except Exception as e:
            print(f"Error listing all ready orders: {e}")
            return []

    @log
    def get_assigned_orders(self, driver_id: int) -> List[Dict[str, Any]]:
        """Retrieve all orders currently being prepared that are assigned to a specific driver.

        Parameters
        ----------
        driver_id : int
            The ID of the driver whose assigned orders are to be retrieved.

        Returns
        -------
        List[Dict[str, Any]]
            A list of dictionaries, each containing:
                - "order": Order object representing the order details.
                - "address": Address object associated with the order.
                - "products": List of dictionaries with product details and quantities.
            Returns an empty list if no assigned orders are found or an error occurs.
        """
        try:
            raw_orders = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_driver = %s AND status = 'Preparing'",
                [driver_id],
                "all",
            )
            return [self.get_by_id(o["id_order"]) for o in raw_orders]
        except Exception as e:
            print(f"Error fetching assigned orders: {e}")
            return []

    @log
    def assign_order(self, id_driver: int, id_order: int) -> bool:
        """Assign a specific order to a driver in the database.

        Parameters
        ----------
        id_driver : int
            The ID of the driver to assign the order to.
        id_order : int
            The ID of the order to be assigned.

        Returns
        -------
        bool
            True if the order was successfully assigned to the driver.
            False if the order does not exist, the assignment fails, or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE orders
                SET id_driver = %s
                WHERE id_order = %s
                RETURNING id_order
                """,
                [id_driver, id_order],
                return_type="one",
            )
            return res is not None
        except Exception as e:
            print(f"Error assigning order to driver: {e}")
            return False

    @log
    def get_orders_by_id_user(self, id_customer: int):
        """Retrieve all orders placed by a specific customer, including their products and address.

        Parameters
        ----------
        id_customer : int
            The ID of the customer whose orders are to be retrieved.

        Returns
        -------
        List[Dict[str, Any]]
            A list of dictionaries, each containing:
                - "order": Order object representing the order details.
                - "address": Address object associated with the order.
                - "products": List of dictionaries with product details and quantities.
            Returns an empty list if the customer has no orders or an error occurs.
        """
        try:
            raw_orders = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_customer = %s", [id_customer], "all"
            )
            result = []
            for o in raw_orders:
                order_data = self.get_by_id(o["id_order"])
                if order_data:
                    result.append(order_data)
            return result
        except Exception as e:
            print(f"Error listing all orders: {e}")
            return []
