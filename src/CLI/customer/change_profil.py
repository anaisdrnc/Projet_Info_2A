from InquirerPy import inquirer

from src.CLI.customer.menu_customer import MenuView
from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Service.UserService import UserService


class ChangeProfileView(AbstractView):
    """Change the customer's password"""

    def choose_menu(self):
        user_repo = UserRepo(DBConnector(test=False))
        user_service = UserService(user_repo)

        choice = inquirer.select(message="Options:", choices=["Change my password", "Go back"]).execute()

        match choice:
            case "Go back":
                return MenuView()

            case "Change my password":
                username = Session().username
                old_password = inquirer.secret(message="Enter your current password:").execute()
                new_password = inquirer.secret(message="Enter your new password:").execute()
                success = user_service.change_password(
                    user_name=username, old_password=old_password, new_password=new_password
                )

                if success:
                    message = "Success"
                    return MenuView(message)

                else:
                    message = "The operation didn't work, please try again."
                    return MenuView(message)
