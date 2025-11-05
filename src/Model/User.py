from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int] = None
    user_name: str
    password: str
    first_name: str
    last_name: str
    email: str
    salt: str
