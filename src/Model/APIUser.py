from pydantic import BaseModel


class APIUser(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
