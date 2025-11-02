from DBConnector import DBConnector
from src.Model.User import User
from src.Model.Customer import Customer

class CustomerDAO():
    def add_customer(
        self
    ):
        with DBConnector().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (first_name, last_name, user_name, password, email)"
                    "VALUES "
                    "(%(first_name)s, %(last_name)s, %(user_name)s, %(password)s, %(email)s)"
                    "RETURNING id_user;",
                    {"last_name" : self.lastname,
                    "first_name" : self.firstname,
                    "user_name": self.username,
                    "password" : self.password,
                    "email" : self.email}
                )
                res = cursor.fetchone()
        print(res)
