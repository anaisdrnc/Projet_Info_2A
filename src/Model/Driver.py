from typing import Literal, Optional

from src.Model.User import User


class Driver(User):
    mean_of_transport: Literal["Bike", "Car"]
    id_driver: Optional[int] = None
