from src.Model.Address import Address
from src.utils.log_decorator import log

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
    """Service class providing operations related to address validation and creation."""

    def __init__(self, addressdao):
        """Initialize the AddressService with a DAO for address persistence.

        Parameters
        ----------
        addressdao : AddressDAO
            DAO responsible for interacting with the address table in the database.
        """
        self.addressdao = addressdao

    @log
    def validate_address(self, address: Address) -> bool:
        """Validate an address based on allowed postal codes and city names.

        An address is considered valid if:
        - its postal code exists in the predefined ALLOWED_ADDRESSES mapping,
        - and the corresponding city matches the provided city.

        Parameters
        ----------
        address : Address
            The address object to validate.

        Returns
        -------
        bool
            True if the address is valid, False otherwise.
        """
        return (
            address.postal_code in ALLOWED_ADDRESSES
            and ALLOWED_ADDRESSES[address.postal_code] == address.city
        )

    @log
    def add_address(self, address, city, postal_code):
        """Create and store a new address in the database.

        Parameters
        ----------
        address : str
            Street name or street address.
        city : str
            City of the address.
        postal_code : int
            Postal code of the address.

        Returns
        -------
        int or bool
            The ID of the newly created address if successful,
            or False if the insertion failed.
        """
        addressdao = self.addressdao
        new_address = Address(address=address, city=city, postal_code=postal_code)
        return addressdao.add_address(new_address)
