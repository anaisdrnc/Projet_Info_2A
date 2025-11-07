from typing import List

from fastapi import APIRouter, HTTPException, status

from src.DAO.DBConnector import DBConnector
from src.Model.Order import Order  # ton modèle Pydantic pour les commandes

order_router = APIRouter(prefix="/Order", tags=["Orders"])
db = DBConnector()

@order_router.get("/", response_model=List[Order], status_code=status.HTTP_200_OK)
def get_all_orders():
    """
    Récupère toutes les commandes depuis la base PostgreSQL.
    """
    try:
        query = 'SELECT * FROM "orders";'  # ou 'SELECT * FROM orders;' selon ton schéma
        orders_data = db.sql_query(query, return_type="all")

        if not orders_data:
            return []  # retourne une liste vide plutôt que None

        # Conversion explicite en objets Pydantic
        return [Order(**order) for order in orders_data]

    except Exception as e:
        print("DEBUG ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )