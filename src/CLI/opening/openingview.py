from InquirerPy import inquirer

from src.CLI.view_abstract import AbstractView


class OpeningView(AbstractView):
    """View displayed when the application is first opened."""

    def choose_menu(self):
        """
        Prompt the user to select the next menu.

        Returns
        -------
        view
            Returns the view chosen by the user in the terminal.
        """

        print("\n" + "-" * 50 + "\nHome\n" + "-" * 50 + "\n")

        choice = inquirer.select(
            message="Please make your choice: ",
            choices=[
                "Login",
                "Create account",
                "Exit",
            ],
        ).execute()

        match choice:
            case "Exit":
                pass

            case "Login":
                from src.CLI.opening.loginview import LoginView

                return LoginView("Log into the application")

            case "Create account":
                from src.CLI.opening.inscriptionview import InscriptionView

                return InscriptionView("Create a customer account")
