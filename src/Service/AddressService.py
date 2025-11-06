from src.Model.Address import Address
from utils.log_decorator import log

ALLOWED_ADDRESSES = {
    35000: "Rennes",
    35170: "Bruz",
    35131: "Chartres de Bretagne",
    35136: "Saint Jacques de la Lande",
    35200: "Rennes",
    35238: "Rennes",
    35700: "Rennes",
}


class AddressService:
    """Class containing address service methods"""
    def __init__(self, addressdao):
        self.addressdao = addressdao

    @log
    def validate_address(self, address : Address) -> bool:
        """Return True if the address is validated"""
        return address.postal_code in ALLOWED_ADDRESSES and ALLOWED_ADDRESSES[address.postal_code] == address.city

    @log
    def add_address(self, address, city, postal_code):
        addressdao = self.addressdao
        new_address = Address(address = address, city = city, postal_code = postal_code)
        return addressdao.add_address(new_address)
        

