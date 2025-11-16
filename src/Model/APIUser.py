from pydantic import BaseModel


class APIUser(BaseModel):
    """
    Class representing a generic API User entity.

    Attributes
    ----------
    id : int
            The unique identifier of the user.
    username : str
            The user's username.
    first_name : str
            The user's first name.
    last_name : str
            The user's last name.
    email : str
            The user's email address.
    """

    id: int
    username: str
    first_name: str
    last_name: str
    email: str
