from fastapi import APIRouter, HTTPException, status

from src.Model.Product import Product

product_router = APIRouter(prefix="/Product", tags=["Menue"])


@product_router.get("/{tmdb_id}", status_code=status.HTTP_200_OK)
def get_menue_by_id(tmdb_id: int):
    try:
        if tmdb_id == 1:
            return Product(
                id=1,
                name="jambon",
                price=12.00,
                production_cost=7.00,
                product_type="lunch",
                description="Bon jambon de Bayonne",
                stock_quantity=78,
            )
        elif tmdb_id == 2:
            return Product(
                id=2,
                name="Pizza",
                price=15.00,
                production_cost=5.00,
                product_type="lunch",
                description="Pizza classique c'est une pizza mais classique quoi",
                stock_quantity=45,
            )
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Product with id [{tmdb_id}] not found"
        )
