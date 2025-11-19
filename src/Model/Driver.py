from typing import Literal, Optional

from Model.User import User


class Driver(User):
    """

    This class extends the base User model, inheriting all core
    user attributes (username, password, name, etc.) and adding
    an attribute specific to the driver role.

    Attributes
    ----------
    mean_of_transport : Bike or Car
                        delivery person's means of transportation

    id_driver : Optional[int]
                The unique identifier for the driver in the database.
                It is optional for creation.
    """

    mean_of_transport: Literal["Bike", "Car"]
    id_driver: Optional[int] = None
