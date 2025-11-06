import logging

from psycopg2 import IntegrityError

from src.DAO.DBConnector import DBConnector
from src.Model.Product import Product
from utils.log_decorator import log

from .DBConnector import DBConnector


class ProductDAO:
    """Class providing access to products in the database"""

    def __init__(self, db_connector=None):
        """Initialize a new DriverDAO instance with a database connector."""
        self.db_connector = db_connector if db_connector is not None else DBConnector()

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
    
    def get_all_products(self):
        """get all products to show the customer"""
        try:
            raw_products = self.db_connector.sql_query("SELECT * FROM product", [], "all")
            result = []
            for o in raw_products:
                product_data = self.get_by_id(o["id_order"])
                if product_data:
                    result.append(product_data)
            return result
        except Exception as e:
            print(f"Error listing all products: {e}")
            return []