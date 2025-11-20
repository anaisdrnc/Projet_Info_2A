from InquirerPy import inquirer

from src.CLI.customer.menu_customer import MenuView
from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite
from src.DAO.DBConnector import DBConnector
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.UserRepo import UserRepo
from src.Model.Customer import Customer
from src.Model.User import User
from src.Service.CustomerService import CustomerService
from src.Service.UserService import UserService


class ChangeProfil(VueAbstraite):
    """change the password of the customer"""

    def choisir_menu(self):

        customerdao = CustomerDAO(DBConnector(test=False))
        customerservice = CustomerService(customerdao)
        userrepo = UserRepo(DBConnector(test=False))
        user_service = UserService(userrepo)

        choice = inquirer.select(
            message= 'Options :',
            choices = ["Change my password", "Go back"]
        ).execute()

        match choice:
            case "Go back":
                return MenuView()

            case "Change my password":
                username = Session().username
                old_password = inquirer.secret(message="Enter your current password : ").execute()
                new_password = inquirer.secret(message= "Enter your new password :").execute()
                works = user_service.change_password(user_name=username, old_password=old_password, new_password=new_password)

                if works :
                    message = "Success"
                    return MenuView(message)

                else :
                    message = "The operation didn't work, please try again."
                    return MenuView(message)