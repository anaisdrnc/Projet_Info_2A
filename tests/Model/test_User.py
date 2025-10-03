import pytest
from pydantic_core import ValidationError

import sys
sys.path.insert(0, '~work/Projet_Info_2A/src/Model')
import unittest
from User import User


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


def test_user_constructor_throws_on_incorrect_input():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id='one',
            username="Lil",
            password="1234password",
            firstname="Lilas",
            lastname="Dupont",
            email="lilas.dpt@gmail.com",
        )
    assert "id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)
