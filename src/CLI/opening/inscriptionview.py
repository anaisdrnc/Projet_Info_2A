import regex
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator

from src.Service.UserService import UserService
from src.Service.CustomerService import CustomerService
from src.CLI.view_abstract import VueAbstraite
from src.DAO.UserRepo import UserRepo
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.Service.PasswordService import check_password_strength


class InscriptionView(VueAbstraite):
    def choisir_menu(self):
        # Demande à l'utilisateur de saisir pseudo, mot de passe...
        pseudo = inquirer.text(message="Enter your username : ").execute()

        user_repo = UserRepo(DBConnector(test=False))
        customerdao = CustomerDAO(DBConnector(test=False))

        user_service = UserService(user_repo)
        customer_service = CustomerService(customerdao=customerdao)

        if user_service.is_username_taken(user_name=pseudo):
            from CLI.opening.openingview import OpeningView

            return OpeningView(f"The username {pseudo} is already used.")

        mdp = inquirer.secret(
            message="Enter your password : ",
            validate=PasswordValidator(
                length=8,
                cap=True,
                number=True,
                message="Au moins 8 caractères, incluant une majuscule, une minuscule et un chiffre",
            ),
        ).execute()

        if not check_password_strength(mdp):
            message = "password not strong enough"
            return OpeningView(message)

        first_name = inquirer.text(message="Enter your firstname : ").execute()

        last_name = inquirer.text(message="Enter your lastname : ").execute()

        mail = inquirer.text(
            message="Entrez votre mail : ", validate=MailValidator()
        ).execute()

        # Appel du service pour créer le joueur
        customer = customer_service.create_customer(
            username=pseudo,
            password=mdp,
            firstname=first_name,
            lastname=last_name,
            email=mail,
        )

        # Si le joueur a été créé
        if customer:
            message = f"Your account {customer.user_name} was successfully created, you can now log in the application"
        else:
            message = "Connection error (invalid username or password)"

        from CLI.opening.openingview import OpeningView

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
