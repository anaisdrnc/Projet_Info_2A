from typing import List, Optional
from datetime import datetime
from src.Model.Order import Order
from src.Model.Address import Address
from src.Model.Product import Product
from src.DAO.DBConnector import DBConnector
from src.Service.AddressService import validate_address


class OrderDAO:
    """DAO final pour la gestion des commandes"""

    def __init__(self, test: bool = False):
        self.db_connector = DBConnector(test=test)

    def create_order(self, order: Order) -> Optional[int]:
        """
        Crée une commande finale après que le client a choisi les produits, l'adresse et le paiement.
        Retourne l'id de la commande ou None si échec.
        """
        try:
            # Vérifier ou insérer l'adresse
            if order.delivery_address.id is None:
                if not validate_address(order.delivery_address):
                    print("Adresse invalide")
                    return None
                # Insérer l'adresse et récupérer son id
                res_addr = self.db_connector.sql_query(
                    """
                    INSERT INTO address (address, city, postal_code)
                    VALUES (%(address)s, %(city)s, %(postalcode)s)
                    RETURNING id_address;
                    """,
                    {
                        "address": order.delivery_address.address,
                        "city": order.delivery_address.city,
                        "postalcode": order.delivery_address.postalcode,
                    },
                    "one",
                )
                if not res_addr:
                    print("Impossible de créer l'adresse")
                    return None
                order.delivery_address.id = res_addr["id_address"]

            # Créer la commande
            res_order = self.db_connector.sql_query(
                """
                INSERT INTO orders (id_customer, id_driver, id_address, date, status,
                                    total_amount, payment_method, nb_items)
                VALUES (%(id_customer)s, %(id_driver)s, %(id_address)s, %(date)s, %(status)s,
                        %(total_amount)s, %(payment_method)s, %(nb_items)s)
                RETURNING id_order;
                """,
                {
                    "id_customer": order.id_customer,
                    "id_driver": order.id_driver,
                    "id_address": order.delivery_address.id,
                    "date": order.date,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "payment_method": order.payment_method,
                    "nb_items": order.nb_items,
                },
                "one",
            )
            if res_order:
                order.id = res_order["id_order"]
                return order.id
            return None

        except Exception as e:
            print(f"Error creating order: {e}")
            return None

    def add_product(self, order_id: int, product_id: int, quantity: int) -> bool:
        """Ajouter un produit à une commande existante"""
        try:
            self.db_connector.sql_query(
                """
                INSERT INTO order_products (id_order, id_product, quantity)
                VALUES (%(order_id)s, %(product_id)s, %(quantity)s)
                ON CONFLICT (id_order, id_product)
                DO UPDATE SET quantity = EXCLUDED.quantity;
                """,
                {"order_id": order_id, "product_id": product_id, "quantity": quantity},
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
                [order_id, product_id],
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
        """Récupérer les commandes en préparation pour un driver"""
        try:
            raw_orders = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_driver = %s AND status = 'Preparing'",
                [driver_id],
                "all",
            )
            return [self._build_order(o) for o in raw_orders]
        except Exception as e:
            print(f"Error fetching assigned orders: {e}")
            return []

    def mark_as_delivered(self, order_id: int) -> bool:
        """Marquer une commande comme livrée"""
        try:
            self.db_connector.sql_query(
                "UPDATE orders SET status = 'Delivered', date = %s WHERE id_order = %s",
                [datetime.now(), order_id],
            )
            return True
        except Exception as e:
            print(f"Error marking order delivered: {e}")
            return False

    def list_all_orders(self) -> List[Order]:
        """Lister toutes les commandes"""
        try:
            raw_orders = self.db_connector.sql_query("SELECT * FROM orders", [], "all")
            return [self._build_order(o) for o in raw_orders]
        except Exception as e:
            print(f"Error listing orders: {e}")
            return []

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Récupérer une commande par son id avec les produits"""
        try:
            raw_order = self.db_connector.sql_query(
                "SELECT * FROM orders WHERE id_order = %s", [order_id], "one"
            )
            if not raw_order:
                return None

            raw_address = self.db_connector.sql_query(
                "SELECT * FROM address WHERE id_address = %s",
                [raw_order["id_address"]],
                "one",
            )
            address = Address(**raw_address) if raw_address else None

            raw_products = self.db_connector.sql_query(
                """
                SELECT p.id_product, p.name, p.price, p.production_cost, 
                       p.product_type, p.description, p.stock, op.quantity
                FROM order_products op
                JOIN product p ON p.id_product = op.id_product
                WHERE op.id_order = %s
                """,
                [order_id],
                "all",
            )

            products = [
                {"product": Product(**p), "quantity": p["quantity"]}
                for p in raw_products
            ]

            total_amount = float(
                sum(float(p["price"]) * p["quantity"] for p in raw_products)
            )

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
                products=products,
            )

        except Exception as e:
            print(f"Error fetching order: {e}")
            return None

    def _build_order(self, raw_order) -> Order:
        """Construire un objet Order à partir des données brutes"""
        raw_address = self.db_connector.sql_query(
            "SELECT * FROM address WHERE id_address = %s",
            [raw_order["id_address"]],
            "one",
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
            nb_items=raw_order["nb_items"],
        )
