from pydantic import BaseModel


class Address(BaseModel):
    """PENSER A CONFIRMER LE FORMAT DES ADRESSES SUR L'API GOOGLE MAPS"""

    address: str
    postalcode: int
    town: str
