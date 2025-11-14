import os
import sys

import dotenv
from psycopg2 import connect, sql

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.DAO.DBConnector import DBConnector

dotenv.load_dotenv()


class ResetDatabase:
    def __init__(self, test: bool = False):
        self.test = test
        self.schema = "test" if test else "default_schema"
        self.sql_file = "data/db_test.sql" if test else "data/db.sql"
        self.db = DBConnector(test=test)

    def lancer(self):
        """Reset the schema by executing the SQL script"""
        print(f"Resetting schema: {self.schema}")
        try:
            with connect(
                host=self.db.host,
                port=self.db.port,
                database=self.db.database,
                user=self.db.user,
                password=self.db.password,
                options=f"-c search_path={self.schema}",
            ) as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    cursor.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(self.schema)))
                    cursor.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))

                    with open(self.sql_file, "r") as f:
                        sql_commands = f.read()
                        cursor.execute(sql_commands)
            print(f"Schema {self.schema} reset successfully!")
        except Exception as e:
            print(f"ERROR resetting schema {self.schema}")
            print(e)
            raise e


if __name__ == "__main__":
    # Exemples d’utilisation
    ResetDatabase(test=False).lancer()  # pour le schéma "default_schema"
    # ResetDatabase(test=True).lancer()  # pour le schéma "test"
