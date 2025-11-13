from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Address import Address
from src.Model.Order import Order

from utils.log_decorator import log


class OrderDAO:
    """DAO pour la gestion des commandes et leurs produits."""

    def __init__(self, db_connector=None):
        """Initialize a new OrderDAO instance with a database connector."""
        self.db_connector = db_connector if db_connector is not None else DBConnector()
        self.productdao = ProductDAO(self.db_connector)

    @log
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

    @log
    def add_product(self, order_id: int, product_id: int, quantity: int = 1) -> bool:
        """
        Ajoute un produit à la commande, décrémente le stock via ProductDAO,
        et met à jour nb_items et total_amount dans orders.
        """
        try:
            # Diminuer le stock
            success = self.productdao.decrement_stock(product_id, quantity)
            if not success:
                logging.warning(f"Stock insuffisant pour le produit {product_id}")
                return False

            # Ajouter le produit à order_products (sans RETURNING et sans fetch)
            self.db_connector.sql_query(
                """
                INSERT INTO order_products (id_order, id_product, quantity)
                VALUES (%s, %s, %s)
                """,
                [order_id, product_id, quantity],
                return_type=None
            )

            # Récupérer le prix du produit
            product = self.db_connector.sql_query(
                "SELECT price FROM product WHERE id_product = %s",
                [product_id],
                "one",
            )
            if not product:
                raise Exception("Produit introuvable pour mise à jour commande")

            total_add = float(product["price"]) * quantity

            # Mettre à jour la commande (nb_items et total_amount)
            self.db_connector.sql_query(
                """
                UPDATE orders
                SET nb_items = COALESCE(nb_items, 0) + %s,
                    total_amount = COALESCE(total_amount, 0) + %s
                WHERE id_order = %s
                """,
                [quantity, total_add, order_id],
                return_type=None
            )

            return True

        except Exception as e:
            logging.error(f"Erreur add_product: {e}")
            # rollback partiel : remettre le stock
            self.productdao.increment_stock(product_id, quantity)
            return False




    @log
    def remove_product(self, order_id: int, product_id: int, quantity: int = 1) -> bool:
        """
        Supprime un produit de la commande, remet le stock,
        et met à jour nb_items et total_amount dans orders.
        """
        try:
            # Vérifier si le produit est bien dans la commande et sa quantité
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

            # Supprimer ou mettre à jour la quantité dans order_products
            if current_qty == remove_qty:
                self.db_connector.sql_query(
                    "DELETE FROM order_products WHERE id_order = %s AND id_product = %s",
                    [order_id, product_id],
                    return_type=None
                )
            else:
                self.db_connector.sql_query(
                    "UPDATE order_products SET quantity = quantity - %s WHERE id_order = %s AND id_product = %s",
                    [remove_qty, order_id, product_id],
                    return_type=None
                )

            # Remettre le stock
            self.productdao.increment_stock(product_id, remove_qty)

            # Récupérer le prix du produit
            product = self.db_connector.sql_query(
                "SELECT price FROM product WHERE id_product = %s",
                [product_id],
                "one",
            )
            total_reduce = float(product["price"]) * remove_qty

            # Mettre à jour la commande (nb_items et total_amount)
            self.db_connector.sql_query(
                """
                UPDATE orders
                SET nb_items = COALESCE(nb_items, 0) - %s,
                    total_amount = COALESCE(total_amount, 0) - %s
                WHERE id_order = %s
                """,
                [remove_qty, total_reduce, order_id],
                return_type=None
            )

            return True

        except Exception as e:
            logging.error(f"Erreur remove_product: {e}")
            return False


    @log
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

    @log
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

    @log
    def mark_as_ready(self, id_order: int) -> bool:
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
    def mark_as_en_route(self, id_order: int) -> bool:
        try:
            res = self.db_connector.sql_query(
                "UPDATE orders SET status='En route', date=%s WHERE id_order=%s RETURNING id_order",
                [datetime.now(), id_order],
                return_type="one",
            )
            return res is not None
        except Exception as e:
            print(f"Error marking order en route: {e}")
            return False

    @log
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


    @log
    def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une commande et les produits associés (sans modifier Order)."""
        try:
            raw_order = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_order = %s", [order_id], "one"
            )
            if not raw_order:
                return None

            # Récupérer l'adresse
            raw_address = self.db_connector.sql_query(
                "SELECT * FROM address WHERE id_address = %s",
                [raw_order["id_address"]],
                "one",
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

    @log
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

    @log
    def list_all_orders_ready(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes prêtes avec leurs produits et l'adresse complète."""
        try:
            # Retrait du hardcodage 'default_schema'
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
        """Récupère les commandes en préparation pour un livreur."""
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
        """Assign the order id_order to the driver id_driver"""
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
