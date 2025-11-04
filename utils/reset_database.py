import os
import logging
import dotenv
import psycopg2

from unittest import mock

from utils.log_decorator import log
from src.DAO.DBConnector import DBConnector

from src.Service.UserService import UserService
from src.DAO.UserRepo import UserRepo


class ResetDatabase():
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
            mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}).start()
            data_path = "data/db_test.sql"
        else:
            data_path = "data/db.sql"

        dotenv.load_dotenv()

        schema = os.environ["POSTGRES_SCHEMA"]

        create_schema = f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"

        init_db = open("data/init_db.sql", encoding="utf-8")
        init_db_as_string = init_db.read()
        init_db.close()

        db = open(data_path, encoding="utf-8")
        db_as_string = db.read()
        db.close()

        try:
            db_connector = DBConnector()
            with psycopg2.connect(
                host=db_connector.host,
                port=db_connector.port,
                database=db_connector.database,
                user=db_connector.user,
                password=db_connector.password,
                options=f"-c search_path={db_connector.schema}",
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(create_schema)
                    cursor.execute(init_db_as_string)
                    cursor.execute(db_as_string)
        except Exception as e:
            logging.info(e)
            raise

        # Applique le hashage des mots de passe aux users
        user_service = UserService(UserRepo())
        all_users = user_service.user_repo.get_all_users(include_password=True)
        for user in all_users:
            user_service.create_user(
                username=user.username,
                password=user.password,
                firstname=user.firstname,
                lastname=user.lastname,
                email=user.email
            )

        logging.info("Base de données réinitialisée avec succès.")
        return True


if __name__ == "__main__":
    ResetDatabase().lancer()
    ResetDatabase().lancer(True)
