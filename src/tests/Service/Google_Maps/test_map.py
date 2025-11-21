from unittest.mock import patch

import pytest

from src.Service.Google_Maps.check_address import (
    check_address,
    get_address_suggestions,
    is_address_sufficient_for_routing,
)


@pytest.fixture
def mock_geocode_valid():
    """Mock for a valid address with city and street"""
    return [
        {
            "formatted_address": "10 Rue de Paris, 75001 Paris, France",
            "address_components": [
                {"types": ["street_number"], "long_name": "10"},
                {"types": ["route"], "long_name": "Rue de Paris"},
                {"types": ["locality"], "long_name": "Paris"},
                {"types": ["postal_code"], "long_name": "75001"},
            ],
        }
    ]


@pytest.fixture
def mock_geocode_only_city():
    """Mock an address with only a city"""
    return [
        {
            "formatted_address": "Paris, France",
            "address_components": [{"types": ["locality"], "long_name": "Paris"}],
        }
    ]


@pytest.fixture
def mock_geocode_vague():
    """Mock for a vague address"""
    return [
        {
            "formatted_address": "France",
            "address_components": [{"types": ["country"], "long_name": "France"}],
        }
    ]


@pytest.fixture
def mock_geocode_empty():
    """Mock for an address not found"""
    return []


def test_check_address_ok(mock_geocode_valid):
    """Address exists and is valid"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_valid,
    ):
        result = check_address("10 Rue de Paris, Paris")

        assert result is True


def test_check_address_ko(mock_geocode_empty):
    """Address does not exist"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_empty,
    ):
        result = check_address("Adresse qui n'existe pas")

        assert result is False


def test_check_address_none():
    """Address is None"""
    result = check_address(None)

    assert result is False


def test_is_address_sufficient_for_routing_with_street_and_city(mock_geocode_valid):
    """Address with street and city is routable"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_valid,
    ):
        is_routable, complete_address = is_address_sufficient_for_routing("10 Rue de Paris, Paris")

        assert is_routable is True
        assert complete_address == "10 Rue de Paris, 75001 Paris, France"


def test_is_address_sufficient_for_routing_only_city(mock_geocode_only_city):
    """Address with only a city is routable"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_only_city,
    ):
        is_routable, complete_address = is_address_sufficient_for_routing("Paris")

        assert is_routable is True
        assert complete_address == "Paris, France"


def test_is_address_sufficient_for_routing_vague_address(mock_geocode_vague):
    """Address too vague not routable"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_vague,
    ):
        is_routable, complete_address = is_address_sufficient_for_routing("France")

        assert is_routable is False
        assert complete_address == "France"


def test_is_address_sufficient_for_routing_empty_address():
    """Empty address"""
    is_routable, complete_address = is_address_sufficient_for_routing("")

    assert is_routable is False
    assert complete_address == ""


def test_get_address_suggestions_ok(mock_geocode_valid):
    """Retrieving address suggestions"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_valid,
    ):
        suggestions = get_address_suggestions("10 Rue de Paris", max_results=3)

        assert len(suggestions) == 1
        assert suggestions[0]["full_address"] == "10 Rue de Paris, 75001 Paris, France"
        assert suggestions[0]["is_routable"] is True
        assert suggestions[0]["street_number"] == "10"
        assert suggestions[0]["street_name"] == "Rue de Paris"
        assert suggestions[0]["city"] == "Paris"
        assert suggestions[0]["postal_code"] == "75001"


def test_get_address_suggestions_empty(mock_geocode_empty):
    """No suggestions found"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_empty,
    ):
        suggestions = get_address_suggestions("Adresse inexistante")

        assert suggestions == []


def test_get_address_suggestions_max_results(mock_geocode_valid):
    """Respecting max_results limit"""
    multiple_results = mock_geocode_valid * 3
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=multiple_results,
    ):
        suggestions = get_address_suggestions("Paris", max_results=2)

        assert len(suggestions) == 2
