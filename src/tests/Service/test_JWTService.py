import datetime
from unittest.mock import patch

import jwt
from freezegun import freeze_time

from src.Service.JWTService import JwtService

jwt_service = JwtService("mysecret")


@freeze_time("2024-08-26 12:00:00")
@patch("src.Service.JWTService.time.time", return_value=datetime.datetime(2024, 8, 26, 12, 0, 0).timestamp())
def test_encode_jwt(mock_time):
    user_id = "myUser"

    jwt_response = jwt_service.encode_jwt(user_id=user_id)
    token = jwt_response.access_token

    decoded = jwt.decode(token, "mysecret", algorithms=["HS256"])

    assert decoded["user_id"] == "myUser"

    expected_ts = datetime.datetime(2024, 8, 26, 12, 20, 0).timestamp()

    assert decoded["expiry_timestamp"] == expected_ts


@freeze_time("2024-08-26 12:00:00")
def test_decode_jwt():
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoibXlVc2VyIiwiZXhwaXJ5X3RpbWVzdGFtcCI6MTcyNDY3NDIwMC4wfQ.eUjNbpMCDNuPESsMHF2dpeRlDl6fMJmjUWsHSZT_n1Q"  # noqa: E501
    decoded_jwt = jwt_service.decode_jwt(jwt)
    assert decoded_jwt.get("user_id") == "myUser"
    assert datetime.datetime.fromtimestamp(decoded_jwt.get("expiry_timestamp")) == datetime.datetime.fromisoformat(
        "2024-08-26 12:10:00"
    )
