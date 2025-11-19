from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite


class MenuDriver(VueAbstraite):
    """Class defining the view of the driver's menu

    Attributes
    ----------
    message='': str

    Returns
    ------
    view
        Returns the next view chosen by the driver in the CLI
    """

    def choisir_menu(self):
        """Seleting the next menu

        Return
        ------
        vue
            Returns the next view chosen by the driver in the CLI
        """

        print("\n" + "-" * 50 + "\nDeliverer's menu\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Make your choice: ",
            choices=[
                "Manage orders",
                "Update my information",
                "Log out",
            ],
        ).execute()

        match choix:
            case "Log out":
                from src.CLI.opening.openingview import OpeningView

                Session.deconnexion()

                return OpeningView()

            case "Manage orders":
                pass
                from src.CLI.driver.manage_order_view import ManageOrderView

                return ManageOrderView()

            case "Update my information":
                from src.CLI.driver.change_profil_driver import ChangeProfilDriver

                return ChangeProfilDriver()
