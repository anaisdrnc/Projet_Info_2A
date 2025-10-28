import pytest
from pydantic_core import ValidationError

from src.Model.User import User


def test_user_constructor_ok():
    User1 = User(
        id=1, username="Lil", password="1234password", firstname="Lilas", lastname="Dupont", email="lilas.dpt@gmail.com"
    )
    assert User1.id == 1
    assert User1.username == "Lil"
    assert User1.password == "1234password"
    assert User1.password == "Lilas"
    assert User1.password == "Dupont"
    assert User1.email == "lilas.dpt@gmail.com"


def test_user_constructor_throws_on_incorrect_id():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id="one",
            username="Lil",
            password="1234password",
            firstname="Lilas",
            lastname="Dupont",
            email="lilas.dpt@gmail.com",
        )
    assert "id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)

def test_user_constructor_throws_on_incorrect_username():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            username=123,
            password="1234password",
            firstname="Lilas",
            lastname="Dupont",
            email="lilas.dpt@gmail.com",
        )
    assert "username" in str(
        exception_info.value
    ) and "Input should be a valid string" in str(exception_info.value)

def test_user_constructor_throws_on_incorrect_firstname():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            username='Lil',
            password="1234password",
            firstname=123,
            lastname="Dupont",
            email="lilas.dpt@gmail.com",
        )
    assert "firstname" in str(
        exception_info.value
    ) and "Input should be a valid string" in str(exception_info.value)

def test_user_constructor_throws_on_incorrect_lastname():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            username='Lil',
            password="1234password",
            firstname='Lilas',
            lastname=True,
            email="lilas.dpt@gmail.com",
        )
    assert "lastname" in str(
        exception_info.value
    ) and "Input should be a valid string" in str(exception_info.value)

def test_user_constructor_throws_on_incorrect_email():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            username='Lil',
            password="1234password",
            firstname='Lilas',
            lastname='Dupont',
            email=[1, 2],
        )
    assert "email" in str(
        exception_info.value
    ) and "Input should be a valid string" in str(exception_info.value)