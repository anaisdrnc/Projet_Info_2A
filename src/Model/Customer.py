from typing import Optional

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)


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
