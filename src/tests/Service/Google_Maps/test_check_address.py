from unittest.mock import patch

import pytest

from src.Service.Google_Maps.map import compute_itinerary, create_map


@pytest.fixture
def mock_directions_valid():
    """Mock pour des directions valides"""
    return [
        {
            "legs": [
                {
                    "duration": {"text": "20 mins", "value": 1200},
                    "distance": {"text": "10 km", "value": 10000},
                    "start_location": {"lat": 48.8566, "lng": 2.3522},
                    "end_location": {"lat": 48.8575, "lng": 2.3533},
                    "steps": [
                        {
                            "html_instructions": "<b>Turn left</b> onto Main St",
                            "distance": {"text": "100 m"},
                            "polyline": {"points": "test_polyline"},
                        },
                        {
                            "html_instructions": "Continue straight",
                            "distance": {"text": "200 m"},
                            "polyline": {"points": "test_polyline_2"},
                        },
                    ],
                }
            ]
        }
    ]


@pytest.fixture
def mock_directions_empty():
    """Mock lorsque aucune direction n'est trouvée"""
    return []


def test_calculer_itineraire_ok(mock_directions_valid):
    """Calcul d'itinéraire réussi"""
    with patch(
        "src.Service.Google_Maps.map.gmaps.directions",
        return_value=mock_directions_valid,
    ):
        result = compute_itinerary("Paris", "Lyon", "driving")

        assert result is not None
        assert result[0]["legs"][0]["duration"]["text"] == "20 mins"


def test_calculer_itineraire_ko(mock_directions_empty):
    """Aucun itinéraire trouvé"""
    with patch(
        "src.Service.Google_Maps.map.gmaps.directions",
        return_value=mock_directions_empty,
    ):
        result = compute_itinerary("Paris", "Adresse invalide", "driving")

        assert result is None


def test_calculer_itineraire_exception():
    """Exception lors du calcul d'itinéraire"""
    with patch(
        "src.Service.Google_Maps.map.gmaps.directions",
        side_effect=Exception("API error"),
    ):
        result = compute_itinerary("Paris", "Lyon", "driving")

        assert result is None


@patch("src.Service.Google_Maps.map.folium.Map")
@patch("src.Service.Google_Maps.map.folium.Marker")
@patch("src.Service.Google_Maps.map.folium.PolyLine")
@patch("src.Service.Google_Maps.map.googlemaps.convert.decode_polyline")
def test_create_map_ok(
    mock_decode_polyline,
    mock_polyline,
    mock_marker,
    mock_map,
    mock_directions_valid,
    tmp_path,
):
    """Création de carte réussie"""
    mock_decode_polyline.return_value = [{"lat": 48.8566, "lng": 2.3522}]

    with patch(
        "src.Service.Google_Maps.map.gmaps.directions",
        return_value=mock_directions_valid,
    ):
        with patch("src.Service.Google_Maps.map.datetime") as mock_datetime:
            mock_datetime.now.return_value = "2024-01-01"

            with patch(
                "src.Service.Google_Maps.map.os.path.dirname",
                return_value=str(tmp_path),
            ):
                with patch(
                    "src.Service.Google_Maps.map.os.path.join",
                    return_value=str(tmp_path / "test_map.html"),
                ):
                    result = create_map("Paris", "Lyon", "driving")

                    assert result == str(tmp_path / "test_map.html")
                    mock_map.assert_called_once()
                    assert mock_marker.call_count == 2
                    mock_polyline.assert_called_once()
