import logging

from src.Model.Address import Address
from src.utils.log_decorator import log


class AddressDAO:
    """Class providing access to the address table of the database"""

    def __init__(self, db_connector):
        """Initialize AddressDAO with a DB connector."""
        self.db_connector = db_connector

    @log
    def add_address(self, address: Address):
        """Add an address to the database

        Parameters
        ----------
        address : Address

        Returns
        -------
        Address or None :
        The Address object with its id_address set if creation succeeds.
        None if the insertion fails or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                """
                INSERT INTO address (address, city, postal_code)
                VALUES (%(address)s, %(city)s, %(postal_code)s)
                RETURNING id_address;
                """,
                {
                    "address": address.address,
                    "city": address.city,
                    "postal_code": address.postal_code,
                },
                return_type="one",
            )

            if res:
                address.id_address = res["id_address"]
                return address
            return None
        except Exception as e:
            logging.info(f"Erreur lors de l'insertion : {e}")
            return None
