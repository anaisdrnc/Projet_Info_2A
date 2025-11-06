from unittest.mock import MagicMock, patch

from src.Model.Address import Address
from src.Model.Order import Order
from src.Service.OrderService import OrderService

### TEST DE ADD


def test_add_product_ok():
    """Ajout d’un produit à la commande réussi"""
    with patch("src.Service.OrderService.OrderDAO.add_product", return_value=True):
        service = OrderService()
        result = service.add(id_order=1, id_product=2, quantity=3)
        assert result is True


def test_add_product_ko_dao_fails():
    """Échec car le DAO retourne False"""
    with patch("src.Service.OrderService.OrderDAO.add_product", return_value=False):
        service = OrderService()
        result = service.add(id_order=1, id_product=2, quantity=3)
        assert result is False


def test_add_product_ko_invalid_quantity():
    """Échec car quantité invalide"""
    service = OrderService()
    result = service.add(id_order=1, id_product=2, quantity=0)
    assert result is False


# TEST DE REMOVE


def test_remove_product_ok():
    """Suppression OK → le DAO retourne True"""
    with patch("src.Service.OrderService.OrderDAO.remove_product", return_value=True):
        service = OrderService()
        result = service.remove(id_order=1, id_product=2, quantity=2)
        assert result is True


def test_remove_product_ko_not_found():
    """Suppression KO → produit pas trouvé dans la commande (DAO retourne False)"""
    with patch("src.Service.OrderService.OrderDAO.remove_product", return_value=False):
        service = OrderService()
        result = service.remove(id_order=1, id_product=2, quantity=10)
        assert result is False


# TEST DE CANCEL ORDER


def test_cancel_order_ok():
    """Annulation réussie → le DAO retourne True"""
    with patch("src.Service.OrderService.OrderDAO.cancel_order", return_value=True):
        service = OrderService()
        result = service.cancel_order(5)
        assert result is True


def test_cancel_order_ko_not_found():
    """Annulation échoue → commande introuvable (DAO retourne False)"""
    with patch("src.Service.OrderService.OrderDAO.cancel_order", return_value=False):
        service = OrderService()
        result = service.cancel_order(999)
        assert result is False


# TEST DE MARK DELIVERED


def test_mark_as_delivered_ok():
    """La commande existe → doit retourner True"""
    with patch("src.Service.OrderService.OrderDAO.mark_as_delivered", return_value=True):
        service = OrderService()
        result = service.mark_as_delivered(10)
        assert result is True


def test_mark_as_delivered_ko():
    """La commande n'existe pas → doit retourner False"""
    with patch("src.Service.OrderService.OrderDAO.mark_as_delivered", return_value=False):
        service = OrderService()
        result = service.mark_as_delivered(999)
        assert result is False


def test_mark_as_delivered_invalid_id():
    service = OrderService()
    assert not service.mark_as_delivered(0)
    assert not service.mark_as_delivered(-5)


# TEST DE GET ORDER PRODUCT


def test_get_order_products_ok():
    """Retourne une liste de produits si la commande existe"""
    fake_products = [
        {"id_product": 1, "name": "Coca", "price": 2.5, "product_type": "drink", "quantity": 2},
        {"id_product": 3, "name": "Panini", "price": 4.0, "product_type": "lunch", "quantity": 1},
    ]

    with patch("src.Service.OrderService.OrderDAO.get_order_products", return_value=fake_products):
        service = OrderService()
        result = service.get_order_products(5)

        assert result == fake_products
        assert isinstance(result, list)
        assert result[0]["name"] == "Coca"


def test_get_order_products_empty():
    """Commande existe mais aucun produit → retourne liste vide"""
    with patch("src.Service.OrderService.OrderDAO.get_order_products", return_value=[]):
        service = OrderService()
        result = service.get_order_products(5)

        assert result == []


def test_get_order_products_invalid_id():
    """ID invalide → doit retourner [] et ne pas appeler le DAO"""
    service = OrderService()
    result = service.get_order_products(0)
    assert result == []

    result = service.get_order_products(-10)
    assert result == []


## TEST DE GET BY ID


def test_get_by_id_ok():
    """Commande existante avec adresse et produits"""
    fake_order = MagicMock(spec=Order)
    fake_address = MagicMock(spec=Address)
    fake_products = [{"id_product": 1, "name": "Coca", "quantity": 2}]

    with patch(
        "src.Service.OrderService.OrderDAO.get_by_id",
        return_value={"order": fake_order, "address": fake_address, "products": fake_products},
    ):
        service = OrderService()
        result = service.get_by_id(5)

        assert result is not None
        assert result["order"] == fake_order
        assert result["address"] == fake_address
        assert result["products"] == fake_products


def test_get_by_id_not_found():
    """Commande introuvable → retourne None"""
    with patch("src.Service.OrderService.OrderDAO.get_by_id", return_value=None):
        service = OrderService()
        result = service.get_by_id(999)
        assert result is None


def test_get_by_id_invalid_id():
    """ID invalide → retourne None sans appeler le DAO"""
    service = OrderService()
    assert service.get_by_id(0) is None
    assert service.get_by_id(-5) is None


### TEST LIST ALL ORDERS


def test_list_all_orders_ok():
    """Retourne une liste de commandes existantes"""
    fake_orders = [
        {"order": MagicMock(), "address": MagicMock(), "products": [{"id_product": 1}]},
        {"order": MagicMock(), "address": MagicMock(), "products": [{"id_product": 2}]},
    ]

    with patch("src.Service.OrderService.OrderDAO.list_all_orders", return_value=fake_orders):
        service = OrderService()
        result = service.list_all_orders()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["products"][0]["id_product"] == 1


def test_list_all_orders_empty():
    """Aucune commande → retourne []"""
    with patch("src.Service.OrderService.OrderDAO.list_all_orders", return_value=[]):
        service = OrderService()
        result = service.list_all_orders()
        assert result == []


### TEST DE GET ASSIGNED DRIVER


def test_get_assigned_orders_ok():
    """Livreur avec commandes → retourne la liste des commandes"""
    fake_orders = [
        {"order": MagicMock(), "address": MagicMock(), "products": [{"id_product": 1}]},
        {"order": MagicMock(), "address": MagicMock(), "products": [{"id_product": 2}]},
    ]

    with patch("src.Service.OrderService.OrderDAO.get_assigned_orders", return_value=fake_orders):
        service = OrderService()
        result = service.get_assigned_orders(5)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["products"][0]["id_product"] == 1


def test_get_assigned_orders_empty():
    """Livreur sans commandes → retourne []"""
    with patch("src.Service.OrderService.OrderDAO.get_assigned_orders", return_value=[]):
        service = OrderService()
        result = service.get_assigned_orders(5)
        assert result == []


def test_get_assigned_orders_invalid_driver():
    """ID livreur invalide → retourne [] sans appeler le DAO"""
    service = OrderService()
    assert service.get_assigned_orders(0) == []
    assert service.get_assigned_orders(-3) == []
