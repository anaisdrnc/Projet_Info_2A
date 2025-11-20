import pytest
from pydantic_core import ValidationError

from src.Model.User import User


def test_user_constructor_ok():
    """Test : Checks that an User object has been initialized correctly."""
    User1 = User(
        id=1,
        user_name="Lil",
        password="1234password",
        first_name="Lilas",
        last_name="Dupont",
        email="lilas.dpt@gmail.com",
        salt="g",
    )
    assert User1.id == 1
    assert User1.user_name == "Lil"
    assert User1.password == "1234password"
    assert User1.first_name == "Lilas"
    assert User1.last_name == "Dupont"
    assert User1.email == "lilas.dpt@gmail.com"
    assert User1.salt == "g"


def test_user_constructor_on_incorrect_id():
    """Test : checks constructor on incorrect id."""
    with pytest.raises(ValidationError) as exception_info:
        User(
            id="one",
            user_name="Lil",
            password="1234password",
            first_name="Lilas",
            last_name="Dupont",
            email="lilas.dpt@gmail.com",
            salt="n",
        )
    assert "id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)


def test_user_constructor_on_incorrect_username():
    """Test : checks constructor on incorrect username."""
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            user_name=123,
            password="1234password",
            first_name="Lilas",
            last_name="Dupont",
            email="lilas.dpt@gmail.com",
            salt="i",
        )
    assert "user_name" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)


def test_user_constructor_on_incorrect_firstname():
    """Test : checks constructor on incorrect firstname."""
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            user_name="Lil",
            password="1234password",
            first_name=123,
            last_name="Dupont",
            email="lilas.dpt@gmail.com",
            salt="h",
        )
    assert "first_name" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)


def test_user_constructor_on_incorrect_lastname():
    """Test : checks constructor on incorrect lastname."""
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            user_name="Lil",
            password="1234password",
            first_name="Lilas",
            last_name=True,
            email="lilas.dpt@gmail.com",
            salt="y",
        )
    assert "last_name" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)


def test_user_constructor_on_incorrect_email():
    """Test : checks constructor on incorrect email."""
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            user_name="Lil",
            password="1234password",
            first_name="Lilas",
            last_name="Dupont",
            email=[1, 2],
            salt="r",
        )
    assert "email" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)
