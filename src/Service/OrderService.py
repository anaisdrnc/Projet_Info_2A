from typing import Any, Dict, List, Optional

from src.DAO.OrderDAO import OrderDAO
from src.Model.Order import Order
from utils.log_decorator import log


class OrderService:
    """Class containing order service methods"""

    @log
    def create(self, id_customer, id_driver, id_address, nb_items, total_amount, payment_method) -> Order:
        """Création d'une commande à partir de ses attributs"""

        new_order = Order(
            id_customer=id_customer,
            id_driver=id_driver,
            id_address=id_address,
            nb_items=nb_items,
            total_amount=total_amount,
            payment_method=payment_method,
        )

        return new_order if OrderDAO().create_order(new_order) else None

    @log
    def add(self, id_order: int, id_product, quantity: int) -> bool:
        """Ajoute un produit à une commande"""
        if quantity <= 0:
            return False  # On refuse les quantités invalides

        return OrderDAO().add_product(id_order, id_product, quantity)

    @log
    def remove(self, id_order: int, id_product, quantity: int) -> bool:
        """Supprime un produit d'une commande"""
        return OrderDAO().remove_product(id_order, id_order)

    @log
    def cancel_order(self, id_order: int) -> bool:
        """Annule une commande"""
        return OrderDAO().cancel_order(id_order)

    @log
    def mark_as_delivered(self, id_order: int) -> bool:
        """Marquer une commande comme livrée"""
        return OrderDAO().mark_as_delivered(id_order)

    @log
    def mark_as_ready(self, id_order: int) -> bool:
        """Marquer une commande comme prête"""
        return OrderDAO().mark_as_ready(id_order)

    @log
    def mark_as_en_route(self, id_order: int) -> bool:
        """Marquer une commande comme en route"""
        return OrderDAO().mark_as_en_route(id_order)

    @log
    def get_order_products(self, id_order: int) -> List[Dict[str, Any]]:
        """Récupère les produits liés à une commande"""
        if id_order <= 0:
            return []
        return OrderDAO().get_order_products(id_order)

    @log
    def get_by_id(self, id_order: int) -> Optional[Dict[str, Any]]:
        """Récupère une commande, son adresse et ses produits"""
        if id_order <= 0:
            return None

        return OrderDAO().get_by_id(id_order)

    @log
    def list_all_orders(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes avec leurs produits"""
        return OrderDAO().list_all_orders()

    @log
    def list_all_orders_ready(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes prêtes avec leurs produits et la date depuis qu'elles sont prêtes"""
        return OrderDAO().list_all_orders_ready()

    @log
    def get_assigned_orders(self, id_driver: int) -> List[Dict[str, Any]]:
        """Récupère les commandes en préparation pour un livreur"""
        if id_driver <= 0:
            return []
        return OrderDAO().get_assigned_orders(id_driver)
