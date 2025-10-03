from typing import Literal
from User import User


class Driver(User):
    transport_mean: Literal["bicycling", "driving"]
