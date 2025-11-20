from unittest.mock import MagicMock

import pytest

from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Admin import Admin
from src.Model.User import User
from src.Service.AdminService import AdminService
from src.utils.reset_database import ResetDatabase
from src.utils.securite import hash_password


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configured for testing"""
    return AdminDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service based on the DAO"""
    return AdminService(admindao=dao)


class TestAdminService:
    """Tests for AdminService"""

    def test_create_ok(self, service):
        """Test: Successfully create a new admin with a strong password"""
        admin = service.create_admin(
            username="JulDjrdn",
            password="Caraibe35",
            first_name="Julie",
            last_name="Dujardin",
            email="julie.dujardin@gmail.com",
        )

        assert admin is not None
        assert isinstance(admin, (Admin, User))
        assert admin.id_admin is not None
        assert admin.user_name == "JulDjrdn"
        assert admin.email == "julie.dujardin@gmail.com"
        assert admin.password != "Caraibe35"
        assert admin.salt is not None

    def test_create_admin_weak_password(self, service):
        """Test: Creating an admin with weak password should raise Exception"""
        with pytest.raises(Exception) as excinfo:
            service.create_admin(
                username="WeakAdmin",
                password="123",
                first_name="Jean",
                last_name="Dupont",
                email="jean.dupont@example.com",
            )
        assert "password" in str(excinfo.value).lower()
        assert "8" in str(excinfo.value)

    def test_get_by_username_ok(self, service):
        """Test: Retrieve an existing admin by username"""
        service.create_admin(
            username="JulDjrdn",
            password="Caraibe35",
            first_name="Julie",
            last_name="Dujardin",
            email="julie.dujardin@gmail.com",
        )
        admin = service.get_by_username("JulDjrdn")
        assert admin is not None
        assert isinstance(admin, Admin)
        assert admin.user_name == "JulDjrdn"
        assert admin.email == "julie.dujardin@gmail.com"

    def test_get_by_username_ko(self, service):
        """Test: Retrieving a non-existent admin should return None"""
        service.admindao.get_by_username = MagicMock(side_effect=Exception("DB error"))
        result = service.get_by_username("inexistant")
        assert result is None

    def test_get_by_id_ok(self, service):
        """Test: Retrieve an existing admin by ID"""
        created = service.create_admin(
            username="TestAdmin",
            password="StrongPass1",
            first_name="Alice",
            last_name="Durand",
            email="aliced@example.com",
        )
        admin = service.get_by_id(created.id_admin)
        assert admin is not None
        assert isinstance(admin, Admin)
        assert admin.id_admin == created.id_admin
        assert admin.user_name == "TestAdmin"

    def test_get_by_id_ko(self, service):
        """Test: Retrieving non-existent admin by ID should return None"""
        service.admindao.get_by_id = MagicMock(side_effect=Exception("DB error"))
        result = service.get_by_id(999)
        assert result is None

    def test_verify_password_ok(self, service):
        """Test: verify_password returns True when the password is correct"""
        pwd = "StrongPass1"
        salt = "selDeTest"
        hashed = hash_password(pwd, salt)
        assert service.verify_password(pwd, hashed, salt) is True

    def test_verify_password_ko(self, service):
        """Test: verify_password returns False when the password is incorrect"""
        pwd = "StrongPass1"
        salt = "selDeTest"
        hashed = hash_password(pwd, salt)
        assert service.verify_password("WrongPassword", hashed, salt) is False
