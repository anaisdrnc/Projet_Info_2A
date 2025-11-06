from datetime import datetime
from typing import Any, Dict, List, Optional

from src.DAO.DBConnector import DBConnector
from src.Model.Address import Address
from src.Model.Order import Order


class OrderDAO:
    """DAO pour la gestion des commandes et leurs produits."""

    def __init__(self, test: bool = False):
        self.db_connector = DBConnector(test=test)

    def create_order(self, order: Order) -> Optional[int]:
        """Crée une nouvelle commande avec l'adresse déjà insérée en base."""
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

    def add_product(self, order_id: int, product_id: int, quantity: int) -> bool:
        try:
            self.db_connector.sql_query(
                """
                INSERT INTO order_products (id_order, id_product, quantity)
                VALUES (%s, %s, %s)
                """,
                [order_id, product_id, quantity],
                return_type=None,
            )
            return True
        except Exception as e:
            print("Error adding product:", e)
            return False

    def remove_product(self, order_id: int, product_id: int) -> bool:
        try:
            res = self.db_connector.sql_query(
                """
                DELETE FROM order_products
                WHERE id_order = %s AND id_product = %s
                RETURNING id_order
                """,
                [order_id, product_id],
                return_type="one",
            )
            return res is not None
        except Exception as e:
            print(f"Error removing product: {e}")
            return False

    def cancel_order(self, id_order: int) -> bool:
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

    def mark_as_delivered(self, id_order: int) -> bool:
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

    def get_order_products(self, order_id: int) -> List[Dict[str, Any]]:
        """Récupère tous les produits liés à une commande."""
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

    def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une commande et les produits associés (sans modifier Order)."""
        try:
            raw_order = self.db_connector.sql_query("SELECT * FROM orders WHERE id_order = %s", [order_id], "one")
            if not raw_order:
                return None

            # Récupérer l'adresse
            raw_address = self.db_connector.sql_query(
                "SELECT * FROM address WHERE id_address = %s", [raw_order["id_address"]], "one"
            )
            address = Address(**raw_address) if raw_address else None

            # Récupérer les produits associés
            products = self.get_order_products(order_id)

            # Construire un objet Order pour la commande
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

    def list_all_orders(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes avec leurs produits."""
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

    def get_assigned_orders(self, driver_id: int) -> List[Dict[str, Any]]:
        """Récupère les commandes en préparation pour un livreur."""
        try:
            raw_orders = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_driver = %s AND status = 'Preparing'", [driver_id], "all"
            )
            return [self.get_by_id(o["id_order"]) for o in raw_orders]
        except Exception as e:
            print(f"Error fetching assigned orders: {e}")
            return []

    
