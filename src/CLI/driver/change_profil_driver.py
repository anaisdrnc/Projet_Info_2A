from InquirerPy import inquirer

from src.CLI.driver.menu_driver import MenuDriver
from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView
from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.DAO.UserRepo import UserRepo
from src.Service.DriverService import DriverService
from src.Service.UserService import UserService
from src.Service.PasswordService import check_password_strength, validate_username_password


class ChangeProfilDriver(AbstractView):
    """
    View for updating a driver's profile, including password and means of transport.
    """

    def choose_menu(self):
        """Main menu for changing driver profile"""
        print("\n" + "="*50)
        print("    Changing driver's profile")
        print("="*50)

        return self.change_driver_profile()

    def change_driver_profile(self):
        """Change driver password or mean of transport"""
        driver_dao = DriverDAO(DBConnector(test=False))
        user_repo = UserRepo(DBConnector(test=False))
        driver_service = DriverService(driver_dao)
        user_service = UserService(user_repo)

        choice = inquirer.select(
            message="Choose an option: ",
            choices=[
                "Change password",
                "Change means of transport",
                "Go back",
            ],
        ).execute()

        match choice:
            case "Go back":
                return MenuDriver()

            case "Change password":
                username = Session().username

                while True:
                    old_password = inquirer.secret(message="Enter your current password:").execute()

                    try:
                        validate_username_password(username, old_password, user_service.user_repo)
                    except Exception:
                        print("Current password is incorrect. Please try again.\n")
                        continue

                    new_password = inquirer.secret(message="Enter your new password:").execute()

                    try:
                        check_password_strength(new_password)
                    except Exception:
                        print("Password invalid. At least 8 characters including uppercase, lowercase, and a number.\n")
                        continue

                    success = user_service.change_password(
                        user_name=username,
                        old_password=old_password,
                        new_password=new_password,
                    )

                    if success:
                        message = "Password successfully changed."
                        break
                    else:
                        print("Operation failed. Please try again.\n")

                return MenuDriver(message)

            case "Change means of transport":
                username = Session().username
                new_transport = inquirer.select(
                    message="Choose your new means of transport:",
                    choices=["Bike", "Car"]
                ).execute()

                success = driver_service.update_driver(username, new_transport)
                message = (
                    "Means of transport successfully changed."
                    if success
                    else "Operation failed, please try again."
                )
                return MenuDriver(message)
