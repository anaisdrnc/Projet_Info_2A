import os
from typing import Literal, Optional, Union

import psycopg2
from dotenv import load_dotenv  #
from psycopg2.extras import RealDictCursor

load_dotenv()  #


class DBConnector:
    def __init__(self, config=None, test: bool = False):
        if config:
            self.host = config["host"]
            self.port = config["port"]
            # self.port = config["post"]
            self.database = config["database"]
            self.user = config["user"]
            self.password = config["password"]
            self.schema = config["schema"]
        else:
            self.host = os.getenv("POSTGRES_HOST", "postgresql-483829")
            self.port = os.getenv("POSTGRES_PORT", "5432")
            self.database = os.getenv("POSTGRES_DB", "defaultdb")
            self.user = os.getenv("POSTGRES_USER", "user-robingirard")
            self.password = os.getenv("POSTGRES_PASSWORD", "")
            # Choix du schema selon si c’est un test
            self.schema = os.getenv("POSTGRES_SCHEMA", "public") if not test else "test"
            """self.host = os.environ["POSTGRES_HOST"]
            self.port = os.environ["POSTGRES_PORT"]
            self.database = os.environ["POSTGRES_DATABASE"]
            self.user = os.environ["POSTGRES_USER"]
            self.password = os.environ["POSTGRES_PASSWORD"]
            # Choix du schema selon si c’est un test
            self.schema = os.environ["POSTGRES_SCHEMA"] if not test else "test" """
        print(f"Connexion DB: {self.user}@{self.host}:{self.port}/{self.database}")

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Union[Literal["one"], Literal["all"]] = "one",
    ):
        try:
            with psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                options=f"-c search_path={self.schema}",
                cursor_factory=RealDictCursor,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, data)
                    if return_type is None:
                        connection.commit()
                        return
                    if return_type == "one":
                        return cursor.fetchone()
                    elif return_type == "all":
                        return cursor.fetchall()
                    elif return_type is None:
                        return cursor.rowcount
        except Exception as e:
            print("ERROR")
            print(e)
            raise e
