import logging
from typing import List, Optional

from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver
from utils.log_decorator import log


class DriverService:
    def __init__(self, driverdao=None):
        self.dao = driverdao if driverdao else DriverDAO()

    @log
    def create_driver(self, driver: Driver) -> bool:
        """Crée un driver via le DAO."""
        try:
            return self.dao.create(driver)
        except Exception as e:
            logging.error(f"Erreur create_driver: {e}")
            return False

    @log
    def get_driver_by_id(self, driver_id: int) -> Optional[Driver]:
        """Retourne un driver par son ID driver."""
        try:
            return self.dao.get_by_id(driver_id)
        except Exception as e:
            logging.error(f"Erreur get_driver_by_id: {e}")
            return None

    @log
    def list_all_drivers(self) -> List[Driver]:
        """Liste tous les drivers."""
        try:
            return self.dao.list_all()
        except Exception as e:
            logging.error(f"Erreur list_all_drivers: {e}")
            return []

    @log
    def update_driver(self, driver: Driver) -> bool:
        """
        Met à jour le driver (mean_of_transport uniquement).
        Les infos utilisateur (nom, mail...) sont gérées par UserService si besoin.
        """
        try:
            return self.dao.update(driver)
        except Exception as e:
            logging.error(f"Erreur update_driver: {e}")
            return False

    @log
    def delete_driver(self, driver_id: int) -> bool:
        """Supprime un driver et son utilisateur."""
        try:
            return self.dao.delete(driver_id)
        except Exception as e:
            logging.error(f"Erreur delete_driver: {e}")
            return False

    @log
    def login(self, username: str, password: str) -> Optional[Driver]:
        """Authentifie un driver."""
        try:
            return self.dao.login(username, password)
        except Exception as e:
            logging.error(f"Erreur login_driver: {e}")
            return None
