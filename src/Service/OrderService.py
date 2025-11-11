from typing import Any, Dict, List, Optional

from src.DAO.OrderDAO import OrderDAO
from src.Model.Order import Order
from utils.log_decorator import log


class OrderService:
    """Classe contenant les méthodes de services pour les commandes"""

    def __init__(self, orderdao: OrderDAO):
        self.orderdao = orderdao

    @log
    def create(self, id_customer, id_address, nb_items, total_amount, payment_method):
        order = Order(
            id_customer=id_customer,
            id_driver=None,
            id_address=id_address,
            nb_items=nb_items,
            total_amount=total_amount,
            payment_method=payment_method,
            status="Preparing"
        )
        order.id_order = self.orderdao.create_order(order)
        if order.id_order:
            return self.get_by_id(order.id_order)
        return None

    @log
    def add_product_to_order(
        self, order_id: int, product_id: int, quantity: int = 1
    ) -> bool:
        """Ajoute un produit à une commande et décrémente le stock"""
        if order_id <= 0 or product_id <= 0 or quantity <= 0:
            return False
        return self.orderdao.add_product(order_id, product_id, quantity)

    @log
    def remove(self, id_order: int, id_product: int, quantity: int = 1) -> bool:
        """Supprime un produit d'une commande et remet le stock"""
        if id_order <= 0 or id_product <= 0 or quantity <= 0:
            return False
        return self.orderdao.remove_product(id_order, id_product, quantity)

    @log
    def cancel_order(self, order_id: int) -> bool:
        """Annule une commande et remet les produits en stock"""
        if order_id <= 0:
            return False

        order_data = self.orderdao.get_by_id(order_id)
        if not order_data:
            return False

        # Remettre les produits en stock
        for p in order_data["products"]:
            self.orderdao.productdao.increment_stock(p["id_product"], p["quantity"])

        return self.orderdao.cancel_order(order_id)

    @log
    def mark_as_delivered(self, id_order: int) -> bool:
        """Marquer une commande comme livrée"""
        if id_order <= 0:
            return False
        return self.orderdao.mark_as_delivered(id_order)

    @log
    def mark_as_ready(self, id_order: int) -> bool:
        """Marquer une commande comme prête"""
        if id_order <= 0:
            return False
        return self.orderdao.mark_as_ready(id_order)

    @log
    def mark_as_en_route(self, id_order: int) -> bool:
        """Marquer une commande comme en route"""
        if id_order <= 0:
            return False
        return self.orderdao.mark_as_en_route(id_order)

    @log
    def get_order_products(self, id_order: int) -> List[Dict[str, Any]]:
        """Récupère les produits liés à une commande"""
        if id_order <= 0:
            return []
        return self.orderdao.get_order_products(id_order)

    @log
    def get_by_id(self, id_order: int) -> Optional[Dict[str, Any]]:
        """Récupère une commande, son adresse et ses produits"""
        if id_order <= 0:
            return None
        return self.orderdao.get_by_id(id_order)

    @log
    def list_all_orders(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes avec leurs produits"""
        return self.orderdao.list_all_orders()

    @log
    def list_all_orders_ready(self) -> List[Dict[str, Any]]:
        """Retourne toutes les commandes prêtes avec leurs produits et l'adresse complète"""
        return self.orderdao.list_all_orders_ready()

    @log
    def get_assigned_orders(self, id_driver: int) -> List[Dict[str, Any]]:
        """Récupère les commandes en préparation pour un livreur"""
        if id_driver <= 0:
            return []
        return self.orderdao.get_assigned_orders(id_driver)

    @log
    def assign_order(self, id_driver: int, id_order: int) -> bool:
        """Assigne une commande à un livreur"""
        if id_driver <= 0 or id_order <= 0:
            return False
        return self.orderdao.assign_order(id_driver, id_order)
