from fastapi import APIRouter, HTTPException, status
from typing import List

from src.Model.Order import Order  # ton modèle Pydantic pour les commandes
from src.DAO.DBConnector import DBConnector

order_router = APIRouter(prefix="/Order", tags=["Orders"])
db = DBConnector()

@order_router.get("/", response_model=List[Order], status_code=status.HTTP_200_OK)
def get_all_orders():
    """
    Récupère toutes les commandes depuis la base PostgreSQL.
    """
    try:
        query = """
            SELECT *
            FROM orders
        """
        orders_data = db.sql_query(query, return_type="all")

        return orders_data

    except Exception as e:
        # Affiche l'erreur exacte dans le log et dans la réponse
        print("DEBUG ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )