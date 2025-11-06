from InquirerPy import inquirer

from src.CLI.view_abstract import VueAbstraite


from src.Service.CustomerService import CustomerService
from src.Service.UserService import UserService


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
                "Log out",
            ],
        ).execute()

        match choix:
            case "Log out":
                from src.CLI.opening.openingview import OpeningView

                return OpeningView()

            case "Place an order":
                pass
                #joueurs_str = JoueurService().afficher_tous()
                #return MenuJoueurVue(joueurs_str)

            case "Get menu":
                from src.CLI.products_view import ProductView

                return ProductView()
