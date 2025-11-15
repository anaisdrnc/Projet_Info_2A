from InquirerPy import inquirer

from src.CLI.customer.menu_customer import MenuView
from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite
from src.DAO.AddressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.OrderDAO import OrderDAO
from src.DAO.ProductDAO import ProductDAO
from src.Service.AddressService import AddressService
from src.Service.OrderService import OrderService
from src.Service.ProductService import ProductService

class OrdersHistory(VueAbstraite):
    def get_history(self):
        orderdao = OrderDAO(DBConnector(test = False))
        order_service = OrderService(orderdao)

        id_customer = Session().id_role

        list_orders = order_service.get_all_orders_by_id_customer(id_customer=id_customer)


