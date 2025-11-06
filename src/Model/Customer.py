from typing import Optional

from src.Model.Address import Address
from src.Model.User import User


class Customer(User):
    address: Optional[Address] = None
    id_customer: int | None = None
