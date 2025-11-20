from typing import List
from typing import Annotated
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter, HTTPException, status, Depends
from src.App.JWTBearer import JWTBearer
from src.DAO.DBConnector import DBConnector
from src.Model.Order import Order  # ton modèle Pydantic pour les commandes
from src.DAO.OrderDAO import OrderDAO
from src.Service.OrderService import OrderService

order_router = APIRouter(prefix="/Order", tags=["Orders"])
db = DBConnector()


@order_router.get("/", status_code=status.HTTP_200_OK)
def get_all_orders(credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]):
    
    """
    Retrieves all orders from the PostgreSQL database.
    """
    orderdao = OrderDAO(DBConnector(test = False))
    order_service = OrderService(orderdao)
    try:
        orders = order_service.list_all_orders()
        return orders

    except Exception as e:
        print("DEBUG ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
