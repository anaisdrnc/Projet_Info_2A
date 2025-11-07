from unittest.mock import MagicMock, Mock, patch

from src.Model.Address import Address
from src.Model.Order import Order
from src.Service.OrderService import OrderService


@pytest.fixture
def mock_dao():
    return Mock()  # Simulates any objects that allows for more flexibility during testing


def test_add_product_ok(mock_dao):
    """Ajout d'un produit à la commande réussi"""
    with patch.object(mock_dao, "add_product", return_value=True):
        service = OrderService(mock_dao)
        result = service.add(1, 2, 3)
        assert result is True


def test_add_product_ko_dao_fails(mock_dao):
    """Échec car le DAO retourne False"""
    with patch.object(mock_dao, "add_product", return_value=False):
        service = OrderService(mock_dao)
        result = service.add(1, 2, 3)
        assert result is False


def test_add_product_ko_invalid_quantity(mock_dao):
    """Échec car quantité invalide"""
    service = OrderService(mock_dao)
    result = service.add(1, 2, 0)  # Quantité invalide
    assert result is False


def test_remove_product_ok(mock_dao):
    """Suppression OK → le DAO retourne True"""
    with patch.object(mock_dao, "remove_product", return_value=True):
        service = OrderService(mock_dao)
        result = service.remove(1, 2)
        assert result is True


def test_remove_product_ko_not_found(mock_dao):
    """Suppression KO → produit pas trouvé dans la commande (DAO retourne False)"""
    with patch.object(mock_dao, "remove_product", return_value=False):
        service = OrderService(mock_dao)
        result = service.remove(1, 2)
        assert result is False


def test_cancel_order_ok(mock_dao):
    """Annulation réussie → le DAO retourne True"""
    with patch.object(mock_dao, "cancel_order", return_value=True):
        service = OrderService(mock_dao)
        result = service.cancel_order(1)
        assert result is True


def test_cancel_order_ko_not_found(mock_dao):
    """Annulation échoue → commande introuvable (DAO retourne False)"""
    with patch.object(mock_dao, "cancel_order", return_value=False):
        service = OrderService(mock_dao)
        result = service.cancel_order(1)
        assert result is False


def test_mark_as_delivered_ok(mock_dao):
    """La commande existe → doit retourner True"""
    with patch.object(mock_dao, "mark_as_delivered", return_value=True):
        service = OrderService(mock_dao)
        result = service.mark_as_delivered(1)
        assert result is True


def test_mark_as_delivered_ko(mock_dao):
    """La commande n'existe pas → doit retourner False"""
    with patch.object(mock_dao, "mark_as_delivered", return_value=False):
        service = OrderService(mock_dao)
        result = service.mark_as_delivered(1)
        assert result is False


def test_mark_as_delivered_invalid_id(mock_dao):
    """ID invalide → doit retourner False"""
    service = OrderService(mock_dao)
    result = service.mark_as_delivered(0)
    assert result is False


def test_get_order_products_ok(mock_dao):
    """Retourne une liste de produits si la commande existe"""
    fake_products = [
        {"id_product": 1, "name": "Coca", "price": 2.5, "product_type": "drink", "quantity": 2},
        {"id_product": 3, "name": "Panini", "price": 4.0, "product_type": "lunch", "quantity": 1},
    ]
    with patch.object(mock_dao, "get_order_products", return_value=fake_products):
        service = OrderService(mock_dao)
        result = service.get_order_products(1)
        assert result == fake_products


def test_get_order_products_empty(mock_dao):
    """Commande existe mais aucun produit → retourne liste vide"""
    with patch.object(mock_dao, "get_order_products", return_value=[]):
        service = OrderService(mock_dao)
        result = service.get_order_products(1)
        assert result == []


def test_get_order_products_invalid_id(mock_dao):
    """ID invalide → doit retourner [] et ne pas appeler le DAO"""
    service = OrderService(mock_dao)
    result = service.get_order_products(0)
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
