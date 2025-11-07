from fastapi import APIRouter, HTTPException, status

from src.DAO.DBConnector import DBConnector
from src.Model.Product import Product

product_router = APIRouter(prefix="/Product", tags=["Products"])

db = DBConnector()


@product_router.get(
    "/{product_id}", response_model=Product, status_code=status.HTTP_200_OK
)
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
                status_code=404, detail=f"Product with id [{product_id}] not found"
            )
        return Product(**product_data)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@product_router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: Product):
    """
    Crée un nouveau produit dans la base PostgreSQL.
    """
    try:
        query = """
            INSERT INTO product (name, price, production_cost, product_type, description, stock)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_product, name, price, production_cost, product_type, description, stock;
        """
        data = (
            product.name,
            product.price,
            product.production_cost,
            product.product_type,
            product.description,
            product.stock,
        )

        new_product = db.sql_query(query, data, return_type="one")

        if not new_product:
            raise HTTPException(status_code=500, detail="Product could not be created")

        return Product(**new_product)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@product_router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int):
    """
    Supprime un produit à partir de son ID depuis la base PostgreSQL.
    """
    try:
        check_query = "SELECT id_product FROM product WHERE id_product = %s;"
        product_exists = db.sql_query(check_query, (product_id,), return_type="one")

        if not product_exists:
            raise HTTPException(
                status_code=404, detail=f"Product with id [{product_id}] not found"
            )

        delete_query = "DELETE FROM product WHERE id_product = %s;"
        db.sql_query(delete_query, (product_id,), return_type=None)

        return {"message": f"Product with id [{product_id}] successfully deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@product_router.put(
    "/{product_id}", response_model=Product, status_code=status.HTTP_200_OK
)
def update_product(product_id: int, updated_product: Product):
    """
    Met à jour un produit existant dans la base PostgreSQL.
    """
    try:
        # Vérifie si le produit existe
        check_query = "SELECT id_product FROM product WHERE id_product = %s;"
        existing_product = db.sql_query(check_query, (product_id,), return_type="one")

        if not existing_product:
            raise HTTPException(
                status_code=404, detail=f"Product with id [{product_id}] not found"
            )

        # Mise à jour du produit
        update_query = """
            UPDATE product
            SET name = %s,
                price = %s,
                production_cost = %s,
                product_type = %s,
                description = %s,
                stock = %s
            WHERE id_product = %s
            RETURNING id_product, name, price, production_cost, product_type, description, stock;
        """

        data = (
            updated_product.name,
            updated_product.price,
            updated_product.production_cost,
            updated_product.product_type,
            updated_product.description,
            updated_product.stock,
            product_id,
        )

        updated_data = db.sql_query(update_query, data, return_type="one")

        if not updated_data:
            raise HTTPException(status_code=500, detail="Product update failed")

        return Product(**updated_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
