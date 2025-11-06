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

class PlaceOrderView(VueAbstraite):
    def choisir_menu(self):
        