from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite


class MenuView(VueAbstraite):
    """Vue du menu du joueur

    Attributes
    ----------
    message=''
        str

    Returns
    ------
    view
        retourne la prochaine vue, celle qui est choisie par l'utilisateur
    """

    def choisir_menu(self):
        """Choix du menu suivant de l'utilisateur

        Return
        ------
        vue
            Retourne la vue choisie par l'utilisateur dans le terminal
        """

        print("\n" + "-" * 50 + "\nMenu Joueur\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Get menu",
                "Place an order",
                "Change profil",
                "Get my orders history",
                "Log out",
            ],
        ).execute()

        match choix:
            case "Log out":
                from CLI.opening.openingview import OpeningView

                Session().deconnexion()

                return OpeningView()

            case "Place an order":
                pass
                from CLI.customer.place_order_view import PlaceOrderView

                return PlaceOrderView()

            case "Get menu":
                from CLI.customer.products_view import ProductView

                return ProductView()

            case "Change profil":
                from CLI.customer.change_profil import ChangeProfil

                return ChangeProfil()

            case "Get my orders history":
                from CLI.customer.orders_history import OrdersHistory

                return OrdersHistory()
