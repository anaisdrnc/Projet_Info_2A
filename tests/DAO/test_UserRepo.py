from typing import TYPE_CHECKING, Literal, Optional, Union

from src.DAO.UserRepo import UserRepo

if TYPE_CHECKING:
    from src.Model.User import User
import os
import pytest
from dotenv import load_dotenv
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from src.DAO.DBConnector import DBConnector

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()

@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    user_dao = UserRepo()
    user_dao.db_connector = DBConnector(test=True)
    return user_dao


def test_add_user_ok(dao):
    user = User(username = "user_test", firstname = "User", lastname = "Test", password = "1234password", "user.test@gmail.com")
    id_user = dao.add_user(user)
    assert id_user > 0




class MockDBConnector:
    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Union[Literal["one"], Literal["all"]] = "one",
    ):
        match query:
            case "SELECT * from users WHERE id=%s":
                if not data:
                    raise Exception
                id_user = data[0]
                return {
                    "id": id_user,
                    "username": "janjak",
                    "password": "myHashedPassword",
                    "salt": "mySalt",
                }


def test_get_user_by_id():
    user_repo = UserRepo(MockDBConnector())
    user: User = user_repo.get_by_id(1)
    assert user is not None
    assert user.id == 1
    assert user.username == "janjak"


def test_integration_get_user_by_id():
    user_repo = UserRepo(DBConnector(config={host: testdb.com}))
    user: User = user_repo.get_by_id(1)
    assert user is not None
    assert user.id == 1
    assert user.username == "janjak"
