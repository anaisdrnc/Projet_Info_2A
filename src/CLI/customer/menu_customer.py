from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView


class MenuView(AbstractView):
    """Customer menu view

    Attributes
    ----------
    message : str
        Optional message to display at the top of the menu.

    Returns
    -------
    AbstractView
        Returns the next view selected by the customer in the CLI.
    """

    def choose_menu(self):
        """Prompt the customer to choose the next action

        Returns
        -------
        VueAbstraite
            Returns the view chosen by the customer in the terminal.
        """

        print("\n" + "-" * 50 + "\nCustomer Menu\n" + "-" * 50 + "\n")

        choice = inquirer.select(
            message="Please make your choice:",
            choices=[
                "Get menu",
                "Place an order",
                "Change profile",
                "Get my orders history",
                "Log out",
            ],
        ).execute()

        match choice:
            case "Log out":
                from src.CLI.opening.openingview import OpeningView

                Session().deconnexion()
                return OpeningView()

            case "Place an order":
                from src.CLI.customer.place_order_view import PlaceOrderView
                return PlaceOrderView()

            case "Get menu":
                from src.CLI.customer.products_view import ProductView
                return ProductView()

            case "Change profile":
                from src.CLI.customer.change_profil import ChangeProfileView
                return ChangeProfileView()

            case "Get my orders history":
                from src.CLI.customer.orders_history import OrdersHistory
                return OrdersHistory()
