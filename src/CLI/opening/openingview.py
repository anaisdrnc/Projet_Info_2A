from InquirerPy import inquirer

from utils.reset_database import ResetDatabase

from src.CLI.view_abstract import VueAbstraite

# from src.CLI.session import Session


class OpeningView(VueAbstraite):
    """View when first opening the application"""

    def choisir_menu(self):
        """Choix du menu suivant

        Return
        ------
        view
            Retourne la vue choisie par l'utilisateur dans le terminal
        """

        print("\n" + "-" * 50 + "\nAccueil\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Login",
                "Create account",
                "Exit",
            ],
        ).execute()

        match choix:
            case "Exit":
                pass

            case "Login":
                from src.CLI.opening.loginview import LoginView

                return LoginView("Log into the application")

            case "Create account":
                from src.CLI.opening.inscriptionview import InscriptionView

                return InscriptionView("Create a customer account")
