import pytest

from src.Model.Driver import Driver


def test_create_valid_driver():
    """Test : création d’un Driver valide"""
    driver = Driver(
        id=1,
        username="emma_driver",
        password="secret",
        firstname="Emma",
        lastname="Glorieux",
        email="emma@test.com",
        transport_mean="driving"
    )

    assert driver.username == "emma_driver"
    assert driver.transport_mean == "driving"
    assert isinstance(driver, Driver)


def test_create_driver_with_bicycle():
    """Test : création d’un Driver avec transport_mean = bicycling"""
    driver = Driver(
        id=2,
        username="paul_bike",
        password="velo",
        firstname="Paul",
        lastname="Martin",
        email="paul@test.com",
        transport_mean="bicycling"
    )

    assert driver.transport_mean == "bicycling"


def test_create_driver_with_invalid_transport_mean():
    """Test : transport_mean invalide"""
    with pytest.raises(ValueError):
        Driver(
            id=3,
            username="bob_invalid",
            password="fail",
            firstname="Bob",
            lastname="Error",
            email="bob@test.com",
            transport_mean="walking"
        )
