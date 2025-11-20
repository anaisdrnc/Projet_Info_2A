import pytest

from src.Model.Driver import Driver


class TestDriver:
    """Tests for the Driver model"""

    def test_create_valid_driver(self):
        """Test : Checks that an Driver object has been initialized correctly."""
        driver = Driver(
            id=1,
            user_name="emma_driver",
            password="secret",
            first_name="Emma",
            last_name="Glorieux",
            email="emma@test.com",
            salt="t",
            mean_of_transport="Car",
        )

        assert driver.user_name == "emma_driver"
        assert driver.mean_of_transport == "Car"
        assert isinstance(driver, Driver)

    def test_create_driver_with_bicycle(self):
        """Test : checks constructor with transport_mean = bike"""
        driver = Driver(
            id=2,
            user_name="paul_bike",
            password="velo",
            first_name="Paul",
            last_name="Martin",
            email="paul@test.com",
            salt="d",
            mean_of_transport="Bike",
        )

        assert driver.mean_of_transport == "Bike"

    def test_create_driver_with_invalid_transport_mean(self):
        """Test : checks constructor with a wrong mean of transport."""
        with pytest.raises(ValueError):
            Driver(
                id=3,
                user_name="bob_invalid",
                password="fail",
                first_name="Bob",
                last_name="Error",
                email="bob@test.com",
                salt="f",
                mean_of_transport="walking",
            )
