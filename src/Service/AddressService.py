from src.Model.Address import Address

ALLOWED_ADDRESSES = {
    35000: "Rennes",
    35170: "Bruz",
    35131: "Chartres de Bretagne",
    35136: "Saint Jacques de la Lande",
    35200: "Rennes",
    35238: "Rennes",
    35700: "Rennes",
}


def validate_address(address: Address) -> bool:
    """Retourne True si l'adresse est valide"""
    return address.postalcode in ALLOWED_ADDRESSES and ALLOWED_ADDRESSES[address.postalcode] == address.city
