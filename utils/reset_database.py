import os
import logging
import dotenv
import psycopg2
from unittest import mock

from utils.log_decorator import log
from src.DAO.DBConnector import DBConnector
from src.Service.UserService import UserService
from src.DAO.UserRepo import UserRepo

class ResetDatabase:
    """
    Réinitialisation de la base de données du projet
    """

    @log
    def lancer(self, test_dao: bool = False):
        """
        Lancement de la réinitialisation de la base :
        If test_dao = True : réinitialisation avec le jeu de données de test
        """
        if test_dao:
            # Change le schéma pour les tests
            mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}).start()
            data_path = "data/db_test.sql"
        else:
            data_path = "data/db.sql"

        dotenv.load_dotenv()
        schema = os.environ.get("POSTGRES_SCHEMA", "public")

        # Création du schema vide
        create_schema_sql = f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"

        # Lecture des scripts SQL
        with open("data/init_db.sql", encoding="utf-8") as f:
            init_db_sql = f.read()
        with open(data_path, encoding="utf-8") as f:
            data_sql = f.read()

        # Connexion à la DB
        db = DBConnector()
        try:
            with psycopg2.connect(
                host=db.host,
                port=db.port,
                database=db.database,
                user=db.user,
                password=db.password,
                options=f"-c search_path={db.schema}",
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(create_schema_sql)
                    cursor.execute(init_db_sql)
                    cursor.execute(data_sql)
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation de la base : {e}")
            raise

        # Recréation des utilisateurs avec hashage des mots de passe
        user_service = UserService(UserRepo())
        all_users = user_service.user_repo.get_all_users(include_password=True)
        for user in all_users:
            try:
                # recrée l'utilisateur avec hash
                user_service.create_user(
                    username=user.username,
                    password=user.password,
                    firstname=user.firstname,
                    lastname=user.lastname,
                    email=user.email
                )
            except Exception as e:
                logging.warning(f"Impossible de recréer l'utilisateur {user.username}: {e}")
                continue

        logging.info("Base de données réinitialisée avec succès.")
        return True


if __name__ == "__main__":
    # Réinitialisation classique
    ResetDatabase().lancer()
    # Réinitialisation pour tests DAO
    ResetDatabase().lancer(True)
