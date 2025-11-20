from InquirerPy import inquirer

from src.CLI.customer.menu_customer import MenuView
from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView
from src.DAO.DBConnector import DBConnector
from src.DAO.OrderDAO import OrderDAO
from src.Service.OrderService import OrderService


class OrdersHistory(AbstractView):
    """View for displaying a customer's past orders"""

    def choose_menu(self):
        order_dao = OrderDAO(DBConnector(test=False))
        order_service = OrderService(order_dao)

        customer_id = Session().id_role

        raw_list_orders = order_service.get_all_orders_by_id_customer(id_customer=customer_id)
        dates_orders = []
        for raw_order in raw_list_orders:
            order = raw_order["order"]
            date = order.date
            if date.date() not in dates_orders:
                dates_orders.append(date.date())

        chosen_date = inquirer.select(
            message="Which date's order history would you like to see?",
            choices=dates_orders
        ).execute()

        message = f"Orders history for {chosen_date}:\n\n"

        for raw_order in raw_list_orders:
            order = raw_order["order"]
            if order.date.date() == chosen_date:
                message += f"Order #{order.id_order}:\n"
                address = raw_order["address"]
                for raw_product in raw_order["products"]:
                    product_name = raw_product["name"]
                    quantity = raw_product["quantity"]
                    message += f"{product_name}, quantity: {quantity}\n"
                message += f"Address: {address.address} {address.city} {address.postal_code}\n"
                message += f"Status: {order.status}\n"
                message += f"Total price: {order.total_amount} euros\n\n"

        return MenuView(message)
