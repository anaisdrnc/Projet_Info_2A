from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite
from src.Service.CustomerService import CustomerService
from src.Service.UserService import UserService


class ChooseOrder(VueAbstraite):
    """Vue du menu du joueur

    Attributes
    ----------
    message=''
        str

    Returns
    ------
    view
        retourne la prochaine vue, celle qui est choisie par l'utilisateur
    """
