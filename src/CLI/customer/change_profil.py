from InquirerPy import inquirer

from CLI.customer.menu_customer import MenuView
from CLI.session import Session
from CLI.view_abstract import VueAbstraite
from DAO.DBConnector import DBConnector
from DAO.CustomerDAO import CustomerDAO
from DAO.UserRepo import UserRepo
from Model.Customer import Customer
from Model.User import User
from Service.CustomerService import CustomerService
from Service.UserService import UserService


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