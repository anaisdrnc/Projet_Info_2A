from typing import List, Optional
from datetime import datetime
from .DBConnector import DBConnector
from src.Model.Order import Order
from src.Model.Address import Address


class OrderDAO:
    """DAO for Orders"""

    def __init__(self):
        """Initialize a new OrderDAO instance with a database connector."""
        self.db_connector = DBConnector()

    def add_order(
        self, order: Order, customer_id: int, driver_id: int
    ) -> Optional[int]:
        """
        Add an order to the database.
        Returns the generated order ID.
        """
        try:
            # Insert order
            res = self.db_connector.sql_query(
                """
                INSERT INTO orders (id_customer, id_driver, id_address, date, status, total_amount, payment_method)
                VALUES (%(id_customer)s, %(id_driver)s, %(id_address)s, %(date)s, %(status)s, %(total_amount)s,
                %(payment_method)s)
                RETURNING id_order;
                """,
                {
                    "id_customer": customer_id,
                    "id_driver": driver_id,
                    "id_address": order.delivery_address.id,
                    "date": order.date,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "payment_method": order.payment_method,
                },
            )
            if res:
                order.id = res["id_order"]
                return order.id
        except Exception as e:
            print(f"Error adding order: {e}")
        return None

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Retrieve an order by its ID"""
        try:
            raw_order = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_order = %s", [order_id], "one"
            )
            if not raw_order:
                return None

            # Fetch the address for the order
            raw_address = self.db_connector.sql_query(
                "SELECT * FROM address WHERE id_address = %s",
                [raw_order["id_address"]],
                "one",
            )
            address = Address(**raw_address) if raw_address else None

            return Order(
                id=raw_order["id_order"],
                date=raw_order["date"],
                status=raw_order["status"],
                delivery_address=address,
                total_amount=float(raw_order["total_amount"]),
                transport_method="car",  # This could be dynamic depending on driver
                payment_method=raw_order["payment_method"],
            )
        except Exception as e:
            print(f"Error fetching order: {e}")
            return None

    def list_all_orders(self) -> List[Order]:
        """Retrieve all orders"""
        orders = []
        try:
            raw_orders = self.db_connector.sql_query("SELECT * FROM orders", [], "all")
            for ro in raw_orders:
                raw_address = self.db_connector.sql_query(
                    "SELECT * FROM address WHERE id_address = %s",
                    [ro["id_address"]],
                    "one",
                )
                address = Address(**raw_address) if raw_address else None

                orders.append(
                    Order(
                        id=ro["id_order"],
                        date=ro["date"],
                        status=ro["status"],
                        delivery_address=address,
                        total_amount=float(ro["total_amount"]),
                        transport_method="car",
                        payment_method=ro["payment_method"],
                    )
                )
        except Exception as e:
            print(f"Error listing orders: {e}")
        return orders

    def delete_order(self, order_id: int) -> bool:
        """Delete an order by ID"""
        try:
            self.db_connector.sql_query(
                "DELETE FROM orders WHERE id_order = %s", [order_id]
            )
            return True
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False

    def update_status(self, order_id: int, new_status: str) -> bool:
        """Update the status of an order"""
        try:
            self.db_connector.sql_query(
                "UPDATE orders SET status = %s WHERE id_order = %s",
                [new_status, order_id],
            )
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False

    def add_product_to_order(
        self, order_id: int, product_id: int, quantity: int
    ) -> bool:
        """Add a product to an order"""
        try:
            self.db_connector.sql_query(
                """
                INSERT INTO order_products (id_order, id_product, quantity)
                VALUES (%(order_id)s, %(product_id)s, %(quantity)s)
                ON CONFLICT (id_order, id_product) DO UPDATE
                SET quantity = EXCLUDED.quantity;
                """,
                {"order_id": order_id, "product_id": product_id, "quantity": quantity},
            )
            return True
        except Exception as e:
            print(f"Error adding product to order: {e}")
            return False

    def remove_product_from_order(self, order_id: int, product_id: int) -> bool:
        """Remove a product from an order"""
        try:
            self.db_connector.sql_query(
                "DELETE FROM order_products WHERE id_order = %s AND id_product = %s",
                [order_id, product_id],
            )
            return True
        except Exception as e:
            print(f"Error removing product from order: {e}")
            return False
