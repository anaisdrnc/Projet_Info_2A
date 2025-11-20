from InquirerPy import inquirer

from src.CLI.view_abstract import VueAbstraite


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
                from CLI.opening.loginview import LoginView

                return LoginView("Log into the application")

            case "Create account":
                from CLI.opening.inscriptionview import InscriptionView

                return InscriptionView("Create a customer account")
