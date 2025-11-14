from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite
from src.Service.CustomerService import CustomerService
from src.Service.UserService import UserService


class MenuDriver(VueAbstraite):
    """Vue du menu du livreur

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

        print("\n" + "-" * 50 + "\nMenu Livreur\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Gérer les commandes",
                "Changer mes informations",
                "Log out",
            ],
        ).execute()

        match choix:
            case "Log out":
                from src.CLI.opening.openingview import OpeningView

                Session.deconnexion()

                return OpeningView()

            case "Gérer les commandes":
                pass
                from src.CLI.manage_order_view import ManageOrderView

                return ManageOrderView()

            case "Changer mes informations":
                from src.CLI.change_profil_driver import ChangeProfilDriver

                return ChangeProfilDriver()
