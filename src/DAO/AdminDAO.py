import logging
from typing import Optional

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Admin import Admin
from utils.securite import hash_password


class AdminDAO:
    """DAO pour gérer les admins dans la base de données."""

    def __init__(self, db_connector=None):
        """Initialise AdminDAO avec un connecteur DB."""
        self.db_connector = db_connector or DBConnector()
        self.user_repo = UserRepo(self.db_connector)

    def add_admin(self, admin: Admin):
        """
        Ajoute un admin dans la base de données.
        1) Crée l'utilisateur dans la table users.
        2) Ajoute l'admin dans la table administrator.
        """
        id_user = self.user_repo.add_user(admin)
        if not id_user:
            return False

        try:
            res = self.db_connector.sql_query(
                "INSERT INTO administrator (id_user) VALUES (%(id_user)s) RETURNING id_administrator;",
                {"id_user": id_user},
            )
        except Exception as e:
            logging.info(e)
            return False

        if res and "id_administrator" in res:
            admin.id_admin = res["id_administrator"]
            return True

        return False

    def login(self, username: str, password: str):
        """
        Authentifie un admin à partir du username et mot de passe.
        Retourne un objet Admin si correct, None sinon.
        """
        try:
            query = """
            SELECT u.id_user, u.user_name, u.password, u.salt, u.first_name, u.last_name, u.email
            FROM users u
            JOIN administrator a ON a.id_user = u.id_user
            WHERE u.user_name = %(username)s
            """
            res = self.db_connector.sql_query(query, {"username": username})
            if not res:
                return None

            # Vérifie le mot de passe
            hashed_input = hash_password(password, res["salt"])
            if hashed_input != res["password"]:
                return None

            admin = Admin(
                id=res["id_user"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
            )
            admin.id_admin = res.get("id_administrator")
            return admin
        except Exception as e:
            logging.info(e)
            return None

    def get_by_username(self, username: str) -> Optional[Admin]:
        """Récupérer un administrateur à partir de son nom d'utilisateur."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT a.id_administrator AS id_admin, u.id_user, u.user_name, u.password, u.salt,
                       u.first_name, u.last_name, u.email
                FROM administrator a
                JOIN users u ON a.id_user = u.id_user
                WHERE u.user_name = %(username)s;
                """,
                {"username": username},
                "one",
            )

            if not res:
                return None

            return Admin(
                id_admin=res["id_admin"],
                id_user=res["id_user"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
            )

        except Exception as e:
            logging.error(f"[AdminDAO] Erreur lors de la récupération de l'admin '{username}': {e}")
            return None
