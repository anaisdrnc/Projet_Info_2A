from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """
    Class representing the User entity in the system.

    Attributes
    ----------
    id : Optional[int]
                The id of the user in the database. Optional for creation.
    user_name : str
                The unique username used for login.
    password : str
                The hashed password of the user.
    first_name : str
                The user's first name.
    last_name : str
                The user's last name.
    email : str
                The user's email address.
    salt : Optional[str]
            The unique cryptographic salt used for password hashing. Optional.
    """

    id: Optional[int] = None
    user_name: str
    password: str
    first_name: str
    last_name: str
    email: str
    # salt: str
    salt: Optional[str] = None
