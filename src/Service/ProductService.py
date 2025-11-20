import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)


from DAO.DBConnector import DBConnector
from DAO.ProductDAO import ProductDAO
from Model.Product import Product
from utils.log_decorator import log


class ProductService:
    """Classe contenant les méthodes de services des produits"""

    def __init__(self, productdao: ProductDAO | None = None):
        """Initialise le service avec un DAO fourni ou par défaut."""
        self.productdao = productdao or ProductDAO(DBConnector())

    @log
    def create(
        self,
        name: str,
        price: float,
        production_cost: float,
        product_type: str,
        description: str,
        stock: int,
    ) -> Product | None:
        """Création d'un produit à partir de ses attributs."""
        new_product = Product(
            name=name,
            price=price,
            production_cost=production_cost,
            product_type=product_type,
            description=description,
            stock=stock,
        )

        new_product = self.productdao.create_product(new_product)
        return new_product

    @log
    def delete(self, product_id: int) -> bool:
        """Supprime un produit par son ID."""
        return self.productdao.deleting_product(product_id)

    @log
    def get_list_products_names(self):
        """Retourne la liste des noms et id de tous les produits."""
        return self.productdao.get_all_product_names()

    @log
    def get_list_products_descriptions(self) -> list[dict]:
        """Retourne les noms et descriptions de tous les produits."""
        return self.productdao.get_all_product_names_descriptions()

    @log
    def get_available_products(self) -> list[dict]:
        """Retourne uniquement les produits dont le stock est supérieur à 0."""
        return self.productdao.get_available_products()

    @log
    def decrement_stock(self, product_id: int, quantity: int = 1) -> bool:
        """Diminue le stock d’un produit."""
        return self.productdao.decrement_stock(product_id, quantity)

    @log
    def increment_stock(self, product_id: int, quantity: int = 1) -> bool:
        """Augmente le stock d’un produit (par exemple après annulation)."""
        return self.productdao.increment_stock(product_id, quantity)

    @log
    def get_id_by_name(self, product_name: str) -> int:
        """Get the id from the name of a product"""
        return self.productdao.get_id_by_productname(product_name)
