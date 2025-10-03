from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    password: str
    firstname: str
    lastname: str
    email: str
