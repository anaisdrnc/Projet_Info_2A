from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    id: Optional[int] = None
    address: str
    postalcode: int
    city: str
