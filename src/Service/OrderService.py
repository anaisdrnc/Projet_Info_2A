from typing import Any, Dict, List, Optional

from src.DAO.OrderDAO import OrderDAO
from src.Model.Order import Order
from utils.log_decorator import log


class OrderService:
    """Class containing order service methods"""

    def __init__(self, orderdao):
        self.orderdao = orderdao

    @log
    def create(self, id_customer, id_driver, id_address, nb_items, total_amount, payment_method) -> Order:
        """Création d'une commande à partir de ses attributs"""
        orderdao = self.orderdao

        new_order = Order(
            id_customer=id_customer,
            id_driver=id_driver,
            id_address=id_address,
            nb_items=nb_items,
            total_amount=total_amount,
            payment_method=payment_method,
        )

        return new_order if orderdao.create_order(new_order) else None

    @log
    def add(self, id_order: int, id_product, quantity: int) -> bool:
        orderdao = self.orderdao

        """Ajoute un produit à une commande"""
        if quantity <= 0:
            return False  # On refuse les quantités invalides

        return orderdao.add_product(id_order, id_product, quantity)

    @log
    def remove(self, id_order: int, id_product, quantity: int) -> bool:
        """Supprime un produit d'une commande"""
        orderdao = self.orderdao

        return orderdao.remove_product(id_order, id_order)

    @log
    def cancel_order(self, id_order: int) -> bool:
        """Annule une commande"""
        orderdao = self.orderdao
        return orderdao.cancel_order(id_order)

    @log
    def mark_as_delivered(self, id_order: int) -> bool:
        """Marquer une commande comme livrée"""
        orderdao = self.orderdao
        return orderdao.mark_as_delivered(id_order)

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
        orderdao = self.orderdao
        if id_order <= 0:
            return []
        return orderdao.get_order_products(id_order)

    @log
    def get_by_id(self, id_order: int) -> Optional[Dict[str, Any]]:
        """Récupère une commande, son adresse et ses produits"""
        orderdao = self.orderdao
        if id_order <= 0:
            return None

        return orderdao.get_by_id(id_order)

    @log
    def list_all_orders(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes avec leurs produits"""
        orderdao = self.orderdao
        return orderdao.list_all_orders()

    @log
    def list_all_orders_ready(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes prêtes avec leurs produits, l'adresse complète de la commande
        et la date depuis qu'elles sont prêtes"""
        return OrderDAO().list_all_orders_ready()

    @log
    def get_assigned_orders(self, id_driver: int) -> List[Dict[str, Any]]:
        """Récupère les commandes en préparation pour un livreur"""
        orderdao = self.orderdao
        if id_driver <= 0:
            return []
        return orderdao.get_assigned_orders(id_driver)
