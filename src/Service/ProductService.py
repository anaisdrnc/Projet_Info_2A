from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from utils.log_decorator import log
from src.DAO.DBConnector import DBConnector


class ProductService:
    """Classe contenant les méthodes de services des produits"""

    def __init__(self, productdao=None):
        self.productdao = productdao or ProductDAO()

    @log
    def create(self, name, price, production_cost, product_type, description, stock) -> Product | None:
        """Création d'un produit à partir de ses attributs"""
        new_product = Product(
            name=name,
            price=price,
            production_cost=production_cost,
            product_type=product_type,
            description=description,
            stock=stock,
        )

        return new_product if self.productdao.create_product(new_product) else None

    @log
    def delete(self, product_id) -> bool:
        """Supprimer un produit"""
        return self.productdao.deleting_product(product_id)

    @log
    def get_list_products_names(self):
        """Liste des noms des produits"""
        return self.productdao.get_all_product_names()

    @log
    def get_list_products_descriptions(self):
        """Liste des noms et descriptions des produits"""
        productdao = self.productdao
        return productdao.get_all_product_names_descriptions()
