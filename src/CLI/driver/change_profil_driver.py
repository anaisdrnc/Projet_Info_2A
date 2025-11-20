from InquirerPy import inquirer

from src.CLI.driver.menu_driver import MenuDriver
from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite
from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.DAO.UserRepo import UserRepo
from src.Service.DriverService import DriverService
from src.Service.UserService import UserService


class ChangeProfilDriver(VueAbstraite):
    """
    Class that defines the view for changing the driver's information about his password or his mean of transport
    """
    def choisir_menu(self):
        """Menu principal de modification du profil"""
        print("\n" + "="*50)
        print("    Changing driver's profile")
        print("="*50)

        return self.change_profil_driver()


    def change_profil_driver(self):
        """view used to change the profil of the drivers, specially their password (since it is the admin
        that create the driver) and the mean of transport"""

        driverdao = DriverDAO(DBConnector(test = False))
        user_repo = UserRepo(DBConnector(test = False))
        driverservice = DriverService(driverdao)
        userservice = UserService(user_repo)

        choice = inquirer.select(
                message="Choose : ",
                choices=[
                    "Change password",
                    "Change the mean of transport",
                    "Go back",
                ],
            ).execute()

        match choice:
            case "Go back":
                return MenuDriver()

            case "Change password":
                username = Session().username
                old_password = inquirer.secret(message="Enter your current password : ").execute()
                new_password = inquirer.secret(message= "Enter your new password :").execute()
                works = userservice.change_password(user_name=username, old_password=old_password,
                new_password=new_password)

                if works :
                    message = "Success"
                    return MenuDriver(message)

                else :
                    message = "The operation didn't work, please try again."
                    return MenuDriver(message)

            case "Change the mean of transport":
                username = Session().username
                new_locomotion = inquirer.select(
                    message="Choose your new mean of transport :",
                    choices= ["Bike", "Car"]
                ).execute()
                works = driverservice.update_driver(username, new_locomotion)
                if works:
                    message = "Your mean of transport has been successfully changed."
                    return MenuDriver(message)

                else :
                    message = "The operation didnt work, please try again."
                    return MenuDriver(message)
