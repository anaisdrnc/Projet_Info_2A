from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    """
    Class representing a physical Address entity.

    Attributes
    ----------
    id_address : Optional[int]
                The primary key of the address in the database. It is optional for creation.
    address : str
                The street name and number
    postal_code : int
                The geographical postal code
    city : str
                The name of the city.
    """

    id_address: Optional[int] = None
    address: str
    postal_code: int
    city: str
