from dao.db_connection import DBConnection


class ProductDAO(metaclass=Singleton):
    def insert_product(
        self,
    ):
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.create()
                pass
