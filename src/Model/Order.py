from typing import Literal
from Address import Address
from datetime import date
from pydantic import BaseModel, Field

class Order(BaseModel):
    id: int
    date: date
    status: Literal["delivered", "waiting"]
    delivery_address: Address
    total_amount: float = Field(..., gt=0, description="The total amount must be strictly positive")
    transport_method: Literal["bicycle", "car"]
    payment_method: Literal["card", "cash"]
