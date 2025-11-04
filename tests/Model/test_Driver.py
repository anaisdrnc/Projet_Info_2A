import pytest

from src.Model.Driver import Driver


def test_create_valid_driver():
    """Test : création d’un Driver valide"""
    driver = Driver(
        id=1,
        user_name="emma_driver",
        password="secret",
        first_name="Emma",
        last_name="Glorieux",
        email="emma@test.com",
        mean_of_transport="Car"
    )

    assert driver.user_name == "emma_driver"
    assert driver.mean_of_transport == "Car"
    assert isinstance(driver, Driver)


def test_create_driver_with_bicycle():
    """Test : création d’un Driver avec transport_mean = bicycling"""
    driver = Driver(
        id=2,
        user_name="paul_bike",
        password="velo",
        first_name="Paul",
        last_name="Martin",
        email="paul@test.com",
        mean_of_transport="Bike"
    )

    assert driver.mean_of_transport == "Bike"


def test_create_driver_with_invalid_transport_mean():
    """Test : mean_of_transport invalide"""
    with pytest.raises(ValueError):
        Driver(
            id=3,
            user_name="bob_invalid",
            password="fail",
            first_name="Bob",
            last_name="Error",
            email="bob@test.com",
            mean_of_transport="walking"
        )
