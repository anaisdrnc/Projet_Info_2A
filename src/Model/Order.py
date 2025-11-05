from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from .Address import Address


class Order(BaseModel):

    id_order: Optional[int] = None
    id_customer: int
    id_driver: int
    delivery_address: Address
    date: datetime = Field(default_factory=datetime.now)
    status: Literal["Delivered", "Preparing"] = "Preparing"
    total_amount: float = Field(..., gt=0)
    payment_method: Literal["card", "cash"]
    nb_items: int = Field(..., ge=0)
    products: Optional[List[dict]] = None
