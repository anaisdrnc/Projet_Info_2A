from datetime import datetime

class Session():
    """Stocke les données liées à une session.
    Cela permet par exemple de connaitre le joueur connecté à tout moment
    depuis n'importe quelle classe.
    Sans cela, il faudrait transmettre ce joueur entre les différentes vues.
    """

    def __init__(self):
        """Création de la session"""
        self.username = None
        self.id_user = None
        self.debut_connexion = None

    def connexion(self, user):
        """Enregistement des données en session"""
        self.username = user.user_name
        self.id_user = user.id_user
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def deconnexion(self):
        """Suppression des données de la session"""
        self.username = None
        self.id_user = None
        self.debut_connexion = None

    def get_id_user(self):
        """return the id of the connected user"""
        return self.id_user