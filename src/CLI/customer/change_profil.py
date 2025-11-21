from InquirerPy import inquirer

from src.CLI.customer.menu_customer import MenuView
from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Service.UserService import UserService
from src.Service.PasswordService import check_password_strength, validate_username_password


class ChangeProfileView(AbstractView):
    """Change the customer's password"""

    def choose_menu(self):
        user_repo = UserRepo(DBConnector(test=False))
        user_service = UserService(user_repo)

        choice = inquirer.select(
            message="Options:",
            choices=["Change my password", "Go back"]
        ).execute()

        match choice:
            case "Go back":
                return MenuView()

            case "Change my password":
                username = Session().username

                while True:
                    # Vérifier l'ancien mot de passe
                    old_password = inquirer.secret(message="Enter your current password:").execute()
                    try:
                        validate_username_password(username, old_password, user_service.user_repo)
                    except Exception:
                        print("Current password is incorrect. Please try again.\n")
                        continue

                    new_password = inquirer.secret(
                        message="Enter your new password:"
                    ).execute()

                    try:
                        check_password_strength(new_password)
                    except Exception:
                        print("Password invalid. At least 8 characters including uppercase, lowercase, and a number.\n")
                        continue

                    success = user_service.change_password(
                        user_name=username,
                        old_password=old_password,
                        new_password=new_password
                    )

                    if success:
                        return MenuView("Your password has been changed successfully!")

                    print("Password change failed. Please try again.\n")
