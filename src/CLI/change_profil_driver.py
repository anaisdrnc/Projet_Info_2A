from InquirerPy import inquirer

from src.CLI.menu_driver import MenuDriver
from src.CLI.view_abstract import VueAbstraite
from src.CLI.session import Session

from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.DAO.UserRepo import UserRepo

from src.Model.Driver import Driver
from src.Model.User import User

from src.Service.DriverService import DriverService

class ChangeProfilDriver(VueAbstraite):
    """view used to change the profil of the drivers, specially their password (since it is the admin
    that create the driver) and the mean of transport"""

    driverdao = DriverDAO(DBConnector(test = False))
    driverservice = DriverService(driverdao)

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
            