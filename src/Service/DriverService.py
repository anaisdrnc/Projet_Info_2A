import logging

from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver
from src.Service.PasswordService import check_password_strength, create_salt
from utils.log_decorator import log
from utils.securite import hash_password


class DriverService:
    def __init__(self, driverdao=None):
        """Initialise le service avec un DAO, ou crée un DriverDAO par défaut"""
        self.driverdao = driverdao if driverdao else DriverDAO()

    @log
    def create_driver(self, username: str, password: str, firstname: str, lastname: str, email: str,
        mean_of_transport: str) -> Driver:
        """Crée un driver avec un mot de passe hashé et le stocke via le DAO"""
        driverdao = self.driverdao
        check_password_strength(password)
        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)
        # Vérifie la force du mot de passe
        check_password_strength(password)

        # Création de l'objet Driver
        driver = Driver(
            user_name=username,
            password=hashed_password,
            salt=salt,
            first_name=firstname,
            last_name=lastname,
            email=email,
            mean_of_transport=mean_of_transport
        )

        if driverdao.create(driver) is not None:
            return driver
        return None


    @log
    def get_by_username(self, username: str) -> Driver | None:
        """Récupère un driver par son nom d'utilisateur"""
        # Parcourt tous les drivers et trouve celui qui correspond
        drivers = self.driverdao.list_all()
        for driver in drivers:
            if driver.user_name == username:
                return driver
        return None

    @log
    def login(self, username: str, password: str) -> Driver | None:
        """Vérifie l'identité d'un driver"""
        driver = self.get_by_username(username)
        if not driver:
            return None

        hashed_input = hash_password(password, driver.salt)
        if hashed_input != driver.password:
            return None

        return driver

    @log
    def update_driver(self, username, locomotion) -> bool:
        """Met à jour les informations du driver (transport uniquement)"""
        assert locomotion in ["Bike", "Car"]
        driver = self.get_by_username(username)
        new_driver = Driver(
            first_name = driver.first_name,
            last_name = driver.last_name,
            user_name = username,
            email = driver.email,
            password = driver.password,
            mean_of_transport = locomotion,
            id = driver.id,
            id_driver = driver.id_driver
        )
        return self.driverdao.update(new_driver)

    @log
    def delete_driver(self, driver_id: int) -> bool:
        """Supprime un driver et son utilisateur associé"""
        return self.driverdao.delete(driver_id)
