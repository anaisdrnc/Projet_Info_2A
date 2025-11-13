from unittest.mock import patch

import pytest

from src.Service.Google_Maps.check_address import (
    check_address,
    get_address_suggestions,
    is_address_sufficient_for_routing,
    validate_and_get_routable_address,
)


@pytest.fixture
def mock_geocode_valid():
    """Mock pour une adresse valide avec rue et ville"""
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
    """Mock pour une adresse avec seulement une ville"""
    return [
        {
            "formatted_address": "Paris, France",
            "address_components": [{"types": ["locality"], "long_name": "Paris"}],
        }
    ]


@pytest.fixture
def mock_geocode_vague():
    """Mock pour une adresse trop vague"""
    return [
        {
            "formatted_address": "France",
            "address_components": [{"types": ["country"], "long_name": "France"}],
        }
    ]


@pytest.fixture
def mock_geocode_empty():
    """Mock pour aucune adresse trouvée"""
    return []


def test_check_address_ok(mock_geocode_valid):
    """Adresse valide existe"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_valid,
    ):
        result = check_address("10 Rue de Paris, Paris")

        assert result is True


def test_check_address_ko(mock_geocode_empty):
    """L'adresse n'existe pas"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_empty,
    ):
        result = check_address("Adresse qui n'existe pas")

        assert result is False


def test_check_address_none():
    """L'adresse est None"""
    result = check_address(None)

    assert result is False


def test_is_address_sufficient_for_routing_with_street_and_city(mock_geocode_valid):
    """Adresse avec rue et ville est routable"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_valid,
    ):
        is_routable, complete_address = is_address_sufficient_for_routing(
            "10 Rue de Paris, Paris"
        )

        assert is_routable is True
        assert complete_address == "10 Rue de Paris, 75001 Paris, France"


def test_is_address_sufficient_for_routing_only_city(mock_geocode_only_city):
    """Adresse avec seulement une ville est routable"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_only_city,
    ):
        is_routable, complete_address = is_address_sufficient_for_routing("Paris")

        assert is_routable is True
        assert complete_address == "Paris, France"


def test_is_address_sufficient_for_routing_vague_address(mock_geocode_vague):
    """Adresse trop vague n'est pas routable"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_vague,
    ):
        is_routable, complete_address = is_address_sufficient_for_routing("France")

        assert is_routable is False
        assert complete_address == "France"


def test_is_address_sufficient_for_routing_empty_address():
    """Adresse vide"""
    is_routable, complete_address = is_address_sufficient_for_routing("")

    assert is_routable is False
    assert complete_address == ""


def test_get_address_suggestions_ok(mock_geocode_valid):
    """Récupération des suggestions d'adresse"""
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
    """Aucune suggestion trouvée"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_empty,
    ):
        suggestions = get_address_suggestions("Adresse inexistante")

        assert suggestions == []


def test_get_address_suggestions_max_results(mock_geocode_valid):
    """Respect de la limite max_results"""
    multiple_results = mock_geocode_valid * 3
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=multiple_results,
    ):
        suggestions = get_address_suggestions("Paris", max_results=2)

        assert len(suggestions) == 2


def test_validate_and_get_routable_address_valid_first_try(mock_geocode_valid):
    """Adresse valide du premier coup"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_valid,
    ):
        with patch("builtins.input", return_value="10 Rue de Paris, Paris"):
            result = validate_and_get_routable_address("Entrez une adresse: ")

            assert result == "10 Rue de Paris, 75001 Paris, France"


def test_validate_and_get_routable_address_user_quits(mock_geocode_vague):
    """L'utilisateur choisit de quitter après adresse invalide"""
    with patch(
        "src.Service.Google_Maps.check_address.gmaps.geocode",
        return_value=mock_geocode_vague,
    ):
        input_responses = ["Adresse vague", "3"]
        with patch("builtins.input", side_effect=input_responses):
            with patch("src.Service.Google_Maps.check_address.display_suggestions"):
                result = validate_and_get_routable_address("Entrez une adresse: ")

                assert result is None
