import regex
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator

from src.Service.UserService import UserService
from src.CLI.view_abstract import VueAbstraite
from src.DAO.UserRepo import UserRepo
from src.DAO.DBConnector import DBConnector


class InscriptionView(VueAbstraite):
    def choisir_menu(self):
        # Demande à l'utilisateur de saisir pseudo, mot de passe...
        pseudo = inquirer.text(message="Enter your username : ").execute()

        user_service = UserService(UserRepo(DBConnector(test = False)))

        if not user_service.is_username_taken(username=pseudo):
            from src.CLI.opening.openingview import OpeningView

            return OpeningView(f"The username {pseudo} is already used.")

        mdp = inquirer.secret(
            message="Enter your password : ",
            validate=PasswordValidator(
                length=35,
                cap=True,
                number=True,
                message="Au moins 35 caractères, incluant une majuscule et un chiffre",
            ),
        ).execute()

        first_name = inquirer.text(message = "Enter your firstname : ").execute()

        last_name = inquirer.text(message = "Enter your lastname : ").execute()

        mail = inquirer.text(message="Entrez votre mail : ", validate=MailValidator()).execute()

        # Appel du service pour créer le joueur
        user = user_service.create_user(username= pseudo, password= mdp, firstname = first_name, lastname= last_name, email = mail)

        # Si le joueur a été créé
        if user:
            message = (
                f"Your account {user.user_name} was successfully created, you can now log in the application"
            )
        else:
            message = "Connection error (invalid username or password)"

        from src.CLI.opening.openingview import OpeningView

        return OpeningView(message)


class MailValidator(Validator):
    """la classe MailValidator verifie si la chaine de caractères
    que l'on entre correspond au format de l'email"""

    def validate(self, document) -> None:
        ok = regex.match(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$", document.text)
        if not ok:
            raise ValidationError(
                message="Please enter a valid mail", cursor_position=len(document.text)
            )
