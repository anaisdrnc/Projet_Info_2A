import regex
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator

from src.Service.OrderService import OrderService
from src.Service.ProductService import ProductService
from src.CLI.view_abstract import VueAbstraite
from src.DAO.ProductDAO import ProductDAO
from src.DAO.OrderDAO import OrderDAO
from src.DAO.DBConnector import DBConnector

class PlaceOrderView(VueAbstraite):
    def choisir_menu(self):
        """Place an order"""
        productdao = ProductDAO(DBConnector)
        orderdao = OrderDAO(DBConnector)
        product_service = ProductService(productdao)
        order_service = OrderService(orderdao)
        
        