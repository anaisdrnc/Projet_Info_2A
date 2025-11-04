from pydantic import BaseModel


class User(BaseModel):
    id: int
    user_name: str
    password: str
    first_name: str
    last_name: str
    email: str
