import logging

from psycopg2 import IntegrityError

from src.DAO.DBConnector import DBConnector
from src.Model.Product import Product
from utils.log_decorator import log

from .DBConnector import DBConnector


class ProductDAO:
    """Class providing access to products in the database"""

    def __init__(self, db_connector):
        """Initialize a new productDAO instance with a database connector."""
        self.db_connector = db_connector

    @log
    def deleting_product(self, id_product: int) -> bool:
        """Deleting a product from the database"""
        try:
            res = self.db_connector.sql_query(
                """
                DELETE FROM product
                WHERE id_product = %(id_product)s
                RETURNING id_product;
                """,
                {"id_product": id_product},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            return False

    @log
    def create_product(self, product: Product) -> bool:
        """Add a product to the database"""
        try:
            res = self.db_connector.sql_query(
                """
                INSERT INTO product (name, price, production_cost, description, product_type, stock)
                VALUES (%(name)s, %(price)s, %(production_cost)s, %(description)s, %(product_type)s, %(stock)s)
                RETURNING id_product;
                """,
                {
                    "name": product.name,
                    "price": product.price,
                    "production_cost": product.production_cost,  # corrigé
                    "description": product.description,
                    "product_type": product.product_type,
                    "stock": product.stock,
                },
                return_type="one",
            )

            if res and "id_product" in res:
                product.id_product = res["id_product"]
                return True
            return False
        except Exception as e:
            logging.info(f"Erreur lors de l'insertion : {e}")
            return False

    @log
    def get_all_products(self):
        """Récupérer tous les produits"""
        try:
            raw_products = self.db_connector.sql_query("SELECT * FROM product", None, "all")
            result = []
            for o in raw_products:
                product_data = Product(
                    id_product=o["id_product"],
                    name=o["name"],
                    price=o["price"],
                    production_cost=o["production_cost"],
                    description=o["description"],
                    product_type=o["product_type"],
                    stock=o["stock"],
                )
                result.append(product_data)
            return result
        except Exception as e:
            logging.info(f"Error listing all products: {e}")
            return []
    
    @log
    def get_all_product_names(self):
        """Retourne juste les noms de tous les produits"""
        try:
            raw = self.db_connector.sql_query("SELECT name FROM product", None, "all")
            return [r["name"] for r in raw]
        except Exception as e:
            logging.info(f"Erreur get_all_product_names: {e}")
            return []

    @log
    def get_all_product_names_descriptions(self):
        """Retourne les noms et descriptions de tous les produits"""
        try:
            raw = self.db_connector.sql_query("SELECT name, description FROM product", [], "all")
            #return [[r["name"], r["description"]] for r in raw]
            return raw
        except Exception as e:
            logging.info(f"Erreur get_all_product_names_descriptions: {e}")
            return []

    @log
    def decrement_stock(self, product_id: int, quantity: int = 1) -> bool:
        """
        Diminue le stock du produit de la quantité spécifiée.
        Retourne True si la mise à jour a réussi, False sinon.
        """
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE product
                SET stock = stock - %s
                WHERE id_product = %s AND stock >= %s
                RETURNING id_product;
                """,
                [quantity, product_id, quantity],
                "one",
            )
            return res is not None
        except Exception as e:
            logging.error(f"Erreur decrement_stock: {e}")
            return False

    def increment_stock(self, product_id: int, quantity: int = 1):
        """Remet du stock si la commande est annulée"""
        try:
            self.db_connector.sql_query(
                "UPDATE product SET stock = stock + %(quantity)s WHERE id_product = %(product_id)s",
                {"quantity": quantity, "product_id": product_id},
                "none"
            )
            return True
        except Exception as e:
            logging.error(f"Erreur increment_stock: {e}")
            return False

    @log
    def get_available_products(self):
        """Retourne uniquement les produits dont le stock est supérieur à 0"""
        try:
            raw = self.db_connector.sql_query("SELECT name, description, price FROM product WHERE stock > 0", [], "all")
            return raw
        except Exception as e:
            logging.info(f"Erreur get_available_products: {e}")
            return []

