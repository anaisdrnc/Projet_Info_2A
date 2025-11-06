import logging

from psycopg2 import IntegrityError

from src.DAO.DBConnector import DBConnector
from src.Model.Product import Product
from utils.log_decorator import log


class ProductDAO:
    """Class providing access to products in the database"""

    def __init__(self):
        """Initialize a new DriverDAO instance with a database connector."""
        self.db_connector = DBConnector()

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
        raw_list = self.db_connector.sql_query("SELECT * FROM product WHERE stock>0")
        if raw_list is None:
            return []
        list_users = []
        for line in raw_list:
            
        
