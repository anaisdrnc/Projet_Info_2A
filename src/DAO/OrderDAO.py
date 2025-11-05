from typing import List, Optional
from datetime import datetime
from src.Model.Order import Order
from src.Model.Address import Address
from src.Model.Product import Product
from src.DAO.DBConnector import DBConnector


class OrderDAO:
    """Data Access Object for managing orders"""

    def __init__(self, test: bool = False):
        self.db_connector = DBConnector(test=test)

    def create_order(self, order: Order) -> Optional[int]:
        """Client crée une commande"""
        try:
            res = self.db_connector.sql_query(
                """
                INSERT INTO orders (id_customer, id_driver, id_address, date, status, total_amount,
                payment_method, nb_items)
                VALUES (%(id_customer)s, %(id_driver)s, %(id_address)s, %(date)s, %(status)s, %(total_amount)s,
                %(payment_method)s, %(nb_items)s)
                RETURNING id_order;
                """,
                {
                    "id_customer": order.id_customer,
                    "id_driver": order.id_driver,
                    "id_address": order.delivery_address.id_address,
                    "date": order.date,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "payment_method": order.payment_method,
                    "nb_items": order.nb_items
                },
                "one"
            )
            if res:
                order.id = res["id_order"]
                return order.id
        except Exception as e:
            print(f"Error creating order: {e}")
        return None

    def add_product(self, order_id: int, product_id: int, quantity: int) -> bool:
        """Ajouter un produit à une commande"""
        try:
            self.db_connector.sql_query(
                """
                INSERT INTO order_products (id_order, id_product, quantity)
                VALUES (%(order_id)s, %(product_id)s, %(quantity)s)
                ON CONFLICT (id_order, id_product)
                DO UPDATE SET quantity = EXCLUDED.quantity;
                """,
                {"order_id": order_id, "product_id": product_id, "quantity": quantity}
            )
            return True
        except Exception as e:
            print(f"Error adding product: {e}")
            return False

    def remove_product(self, order_id: int, product_id: int) -> bool:
        """Retirer un produit du panier"""
        try:
            self.db_connector.sql_query(
                "DELETE FROM order_products WHERE id_order = %s AND id_product = %s",
                [order_id, product_id]
            )
            return True
        except Exception as e:
            print(f"Error removing product: {e}")
            return False

    def cancel_order(self, order_id: int) -> bool:
        """Annuler une commande"""
        try:
            self.db_connector.sql_query(
                "DELETE FROM orders WHERE id_order = %s", [order_id]
            )
            return True
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return False

    def get_assigned_orders(self, driver_id: int) -> List[Order]:
        """Obtenir les commandes assignées à un driver"""
        try:
            raw_orders = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_driver = %s AND status = 'Preparing'",
                [driver_id],
                "all"
            )
            return [self._build_order(o) for o in raw_orders]
        except Exception as e:
            print(f"Error fetching assigned orders: {e}")
            return []

    def mark_as_delivered(self, order_id: int) -> bool:
        """Driver marque une commande comme livrée"""
        try:
            self.db_connector.sql_query(
                "UPDATE orders SET status = 'Delivered', date = %s WHERE id_order = %s",
                [datetime.now(), order_id]
            )
            return True
        except Exception as e:
            print(f"Error marking order delivered: {e}")
            return False

    def list_all_orders(self) -> List[Order]:
        """Lister toutes les commandes (admin)"""
        try:
            raw_orders = self.db_connector.sql_query("SELECT * FROM orders", [], "all")
            return [self._build_order(o) for o in raw_orders]
        except Exception as e:
            print(f"Error listing orders: {e}")
            return []

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Retrieve an order by its ID with product details"""
        try:
            raw_order = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_order = %s", [order_id], "one"
            )
            if not raw_order:
                return None

            # Get address info
            raw_address = self.db_connector.sql_query(
                "SELECT * FROM address WHERE id_address = %s",
                [raw_order["id_address"]],
                "one"
            )
            address = Address(**raw_address) if raw_address else None

            # Get products in the order
            raw_products = self.db_connector.sql_query(
                """
                SELECT p.id_product, p.name, p.price, p.production_cost, 
                       p.product_type, p.description, p.stock, op.quantity
                FROM order_products op
                JOIN product p ON p.id_product = op.id_product
                WHERE op.id_order = %s
                """,
                [order_id],
                "all"
            )

            products = [
                {"product": Product(**p), "quantity": p["quantity"]}
                for p in raw_products
            ]

            # Calculate total dynamically
            total_amount = float(sum(float(p["price"]) * p["quantity"] for p in raw_products))

            return Order(
                id=raw_order["id_order"],
                id_customer=raw_order["id_customer"],
                id_driver=raw_order["id_driver"],
                delivery_address=address,
                date=raw_order["date"],
                status=raw_order["status"],
                total_amount=total_amount,
                payment_method=raw_order["payment_method"],
                nb_items=len(raw_products),
                products=products
            )

        except Exception as e:
            print(f"Error fetching order: {e}")
            return None

    def _build_order(self, raw_order) -> Order:
        """Construit un objet Order complet à partir des données SQL"""
        raw_address = self.db_connector.sql_query(
            "SELECT * FROM address WHERE id_address = %s",
            [raw_order["id_address"]],
            "one"
        )
        address = Address(**raw_address) if raw_address else None

        return Order(
            id=raw_order["id_order"],
            id_customer=raw_order["id_customer"],
            id_driver=raw_order.get("id_driver"),
            delivery_address=address,
            date=raw_order["date"],
            status=raw_order["status"],
            total_amount=float(raw_order["total_amount"]),
            payment_method=raw_order["payment_method"],
            nb_items=raw_order["nb_items"]
        )
