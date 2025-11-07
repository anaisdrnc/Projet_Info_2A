from InquirerPy import inquirer

from src.CLI.view_abstract import VueAbstraite
from src.DAO.ProductDAO import ProductDAO
from src.DAO.DBConnector import DBConnector
from src.Service.ProductService import ProductService


class ProductView(VueAbstraite):
    """View that shows :
    - the list of products available with description
    """

    def choisir_menu(self):
        productdao = ProductDAO(DBConnector)
        productservice = ProductService(productdao)

        list_products = productservice.get_list_products_descriptions()

        from src.CLI.menu_customer import MenuView

        products_str = f"Liste des produits disponibles : \n\n"
        products_str += str(list_products)
        return MenuView(products_str)
