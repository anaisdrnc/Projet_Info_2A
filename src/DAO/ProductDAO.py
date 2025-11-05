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
    def deleting_product(self, product) -> bool:
        """Deleting a product from the database

        Parameters
        ----------
        product: Product
            product to be deleted from the database

        Returns
        -------
            True if the product has been successfully deleted
        """

        res = None
        try:
            res = self.db_connector.sql_query(
                "DELETE FROM product WHERE id_product = %(id_product)s RETURNING id_product",
                {"id_product": product.id_product},
                return_type="one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            raise

        return res > 0

    @log
    def add_product(self, product: Product) -> bool:
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
                    "production_cost": product.production_cost,
                    "description": product.description,
                    "product_type": product.product_type,
                    "stock": product.stock,
                },
                return_type="one",
            )
            if res:
                product.id_product = res["id_product"]
                return True
            return False
        except IntegrityError:
            # Violation de contrainte, ex: nom déjà existant
            return False
        except Exception as e:
            logging.error(f"Erreur ajout produit: {e}")
            return False
