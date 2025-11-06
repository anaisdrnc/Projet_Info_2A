from InquirerPy import inquirer

from src.CLI.view_abstract import VueAbstraite
#from src.CLI.session import Session

from src.DAO.UserRepo import UserRepo
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector

from src.Service.UserService import UserService
from src.Service.CustomerService import CustomerService
from src.Service.PasswordService import validate_username_password


class LoginView(VueAbstraite):
    """Vue de Connexion (saisie de pseudo et mdp)"""

    def choisir_menu(self):

        user_repo = UserRepo(DBConnector(test = False))
        customerdao = CustomerDAO(DBConnector(test = False))

        # Demande à l'utilisateur de saisir pseudo et mot de passe
        pseudo = inquirer.text(message="Enter your username : ").execute()
        mdp = inquirer.secret(message="Enter your password :").execute()

        # Appel du service pour trouver le joueur
        user = validate_username_password(username= pseudo, password= mdp, user_repo = user_repo)

        # Si le joueur a été trouvé à partir des ses identifiants de connexion
        if user:
            message = f"You are connected on the account {user.user_name}"
            #Session().connexion(joueur)

            #from view.menu_joueur_vue import MenuJoueurVue

            #return MenuJoueurVue(message)

        message = "Erreur de connexion (pseudo ou mot de passe invalide)"
        from src.CLI.opening.openingview import OpeningView

        return OpeningView(message)