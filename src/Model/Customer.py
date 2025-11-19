from typing import Optional

from Model.Address import Address
from Model.User import User


class Customer(User):
    """
    Class representing a Customer user.

    This class extends the base User model, inheriting all core
    user attributes (username, password, name, etc.) and adding
    an attribute specific to the customer role.

    Attributes
    ----------
    address : Optional[Address]
                It is optional for creation.
    id_customer : Optional[int]
                The unique identifier for the customer in the database.
                It is optional for creation.
    """

    address: Optional[Address] = None
    id_customer: Optional[int] = None
