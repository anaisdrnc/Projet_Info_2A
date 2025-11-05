from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    id_address: Optional[int] = None
    address: str
    postal_code: int
    city: str
