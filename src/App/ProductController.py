from fastapi import APIRouter, HTTPException, status

from src.Model.Product import Product
from src.DAO.DBConnector import DBConnector
product_router = APIRouter(prefix="/Product", tags=["Menu"])

# Initialisation du connecteur (tu peux aussi en faire une dépendance)
db = DBConnector()

@product_router.get("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
def get_product_by_id(product_id: int):
    """
    Récupère un produit à partir de son ID depuis la base PostgreSQL.
    """
    try:
        query = """
            SELECT 
                id_product,
                name,
                price,
                production_cost,
                product_type,
                description,
                stock
            FROM product
            WHERE id_product = %s;
        """
        product_data = db.sql_query(query, (product_id,), return_type="one")

        if not product_data:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id [{product_id}] not found"
            )

        # Retourne un objet Pydantic à partir du dict
        return Product(**product_data)

    except HTTPException:
        # Laisse passer les exceptions HTTP normales
        raise

    except Exception as e:
        # Capture seulement les erreurs de DB réelles
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )