from datetime import datetime
from utils.log_decorator import log
from utils.singleton import Singleton

class Session(metaclass = Singleton):
    """Stocke les données liées à une session.
    Cela permet par exemple de connaitre le joueur connecté à tout moment
    depuis n'importe quelle classe.
    Sans cela, il faudrait transmettre ce joueur entre les différentes vues.
    """

    def __init__(self):
        """Création de la session"""
        self.username = None
        self.id_role = None
        self.debut_connexion = None

    @log
    def connexion(self, user, id_role):
        """Enregistement des données en session"""
        self.username = user.user_name
        self.id_role = id_role
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    @log
    def deconnexion(self):
        """Suppression des données de la session"""
        self.username = None
        self.id_role = None
        self.debut_connexion = None

    @log
    def get_id_role(self):
        """return the id of the connected user"""
        return self.id_role
