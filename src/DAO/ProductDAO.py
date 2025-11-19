import logging

from src.Model.Product import Product
from utils.log_decorator import log


class ProductDAO:
    """Class providing access to the Product table of the database"""

    def __init__(self, db_connector):
        """Initialize ProductDAO with a DB connector."""
        self.db_connector = db_connector

    @log
    def deleting_product(self, id_product: int) -> bool:
        """Delete a product from the database by its ID.

        Parameters
        ----------
        id_product : int
            The unique identifier of the product to delete.

        Returns
        -------
        bool
            True if the product was successfully deleted.
            False if the product does not exist or an error occurs."""
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
        """Create a new product in the database.

        Parameters
        ----------
        product : Product
            The product that will be created in the database.

        Returns
        -------
        bool
            True if the product was successfully created and assigned an ID.
            False if the insertion fails or an error occurs."""
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

            if res and "id_product" in res:
                product.id_product = res["id_product"]
                return True
            return False
        except Exception as e:
            logging.info(f"Erreur lors de l'insertion : {e}")
            return False

    @log
    def get_all_products(self):
        """Retrieve all products stored in the database.

        Returns
        -------
        List[Product]
            A list of Product instances representing all products in the database.
            Returns an empty list if an error occurs.
        """
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
        """Retrieve the names of all products.

        Returns
        -------
        List[str]
            A list of product names. Returns an empty list if an error occurs.
        """
        try:
            raw = self.db_connector.sql_query("SELECT name FROM product", None, "all")
            return [r["name"] for r in raw]
        except Exception as e:
            logging.info(f"Erreur get_all_product_names: {e}")
            return []

    @log
    def get_all_product_names_descriptions(self):
        """Retrieve the names and descriptions of all products.

        Returns
        -------
        List[Dict[str, Any]]
            A list of dicts with keys "name" and "description".
            Returns an empty list if an error occurs."""
        try:
            raw = self.db_connector.sql_query("SELECT name, description FROM product", [], "all")
            # return [[r["name"], r["description"]] for r in raw]
            return raw
        except Exception as e:
            logging.info(f"Erreur get_all_product_names_descriptions: {e}")
            return []

    @log
    def decrement_stock(self, product_id: int, quantity: int = 1) -> bool:
        """Decreases the available stock of a product.

        Parameters
        ----------
        product_id : int
            The unique identifier of the product whose stock should be decreased.
        quantity : int, optional
            The amount to subtract from the current stock (default is 1).

        Returns
        -------
        bool
            True if the stock update succeeded (product exists and has enough stock).
            False if the update failed.

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
        """Increases the stock level of a product.

        Parameters
        ----------
        product_id : int
            The unique identifier of the product whose stock should be increased.
        quantity : int, optional
            The number of units to add back to the stock (default is 1).

        Returns
        -------
        bool
            True if the stock was successfully updated.
            False if a database error occurred."""
        try:
            self.db_connector.sql_query(
                "UPDATE product SET stock = stock + %(quantity)s WHERE id_product = %(product_id)s",
                {"quantity": quantity, "product_id": product_id},
                "none",
            )
            return True
        except Exception as e:
            logging.error(f"Erreur increment_stock: {e}")
            return False

    @log
    def get_available_products(self):
        """Retrieve all products that are currently in stock.

        Returns
        -------
        list[dict]
            A list of dictionaries, each containing the fields:
            - name
            - description
            - price
            - product_type
            - stock

        Returns an empty list if no products are available or if an error occurs."""
        try:
            raw = self.db_connector.sql_query(
                "SELECT name, description, price, product_type, stock FROM product WHERE stock > 0",
                [],
                "all",
            )
            return raw
        except Exception as e:
            logging.info(f"Erreur get_available_products: {e}")
            return []

    @log
    def get_id_by_productname(self, product_name: str):
        """Retrieve the product ID for a given product name.

        Parameters
        ----------
        product_name : str
            The name of the product to look up.

        Returns
        -------
        Optional[int]
            The id_product if found, otherwise None.
        """
        raw_id = self.db_connector.sql_query("SELECT id_product from product WHERE name=%s", [product_name], "one")
        if raw_id is None:
            return None
        return raw_id["id_product"]
