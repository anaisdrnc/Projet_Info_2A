from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView


class MenuDriver(AbstractView):
    """View for the driver's menu.

    Attributes
    ----------
    message : str
        Optional message to display at the top of the menu.

    Returns
    -------
    VueAbstraite
        Returns the next view selected by the driver in the CLI.
    """

    def choose_menu(self):
        """Display the driver menu and prompt for the next action.

        Returns
        -------
        VueAbstraite
            Returns the next view selected by the driver in the CLI.
        """

        print("\n" + "-" * 50 + "\nDriver Menu\n" + "-" * 50 + "\n")

        choice = inquirer.select(
            message="Make your choice: ",
            choices=[
                "Manage orders",
                "Update my information",
                "Log out",
            ],
        ).execute()

        match choice:
            case "Log out":
                from CLI.opening.openingview import OpeningView

                Session().logout()
                return OpeningView()

            case "Manage orders":
                from CLI.driver.manage_order_view import ManageOrderView
                return ManageOrderView()

            case "Update my information":
                from CLI.driver.change_profil_driver import ChangeProfilDriver
                return ChangeProfilDriver()
