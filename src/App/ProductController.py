from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.App.JWTBearer import JWTBearer
from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from src.Service.ProductService import ProductService

product_router = APIRouter(prefix="/Product", tags=["Products"])
db = DBConnector()


@product_router.get("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
def get_product_by_id(product_id: int, credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]):
    """Retrieve a product by its ID."""
    productdao = ProductDAO(DBConnector(test=False))
    try:
        product = productdao.get_product_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product with id [{product_id}] not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e


@product_router.get("/id/{product_name}", status_code=status.HTTP_200_OK)
def get_all_products(product_name, credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]):
    """Gives all products with id so that the admin can use the others endpoints"""
    productdao = ProductDAO(DBConnector(test=False))
    product_service = ProductService(productdao)
    try:
        id_product = product_service.get_id_by_name(product_name)
        return id_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e


@product_router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    name,
    price,
    description,
    production_cost,
    product_type,
    stock,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],  # admin connecté
):
    """Create a new product (admin only)."""
    productdao = ProductDAO(DBConnector(test=False))
    product_service = ProductService(productdao)
    try:
        new_product = product_service.create(
            name=name,
            price=price,
            production_cost=production_cost,
            product_type=product_type,
            description=description,
            stock=stock,
        )
        if new_product is None:
            raise HTTPException(status_code=500, detail="Product could not be created")
        return new_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e


@product_router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],  # admin connecté
):
    """Delete a product by ID (admin only)."""
    productdao = ProductDAO(DBConnector(test=False))
    product_service = ProductService(productdao)
    try:
        deleted = product_service.delete(product_id)
        if deleted:
            return {"message": f"Product with id [{product_id}] successfully deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e


@product_router.put("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    updated_product: Product,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],  # admin connecté
):
    """Update an existing product (admin only)."""
    try:
        check_query = "SELECT id_product FROM product WHERE id_product = %s;"
        existing_product = db.sql_query(check_query, (product_id,), return_type="one")
        if not existing_product:
            raise HTTPException(status_code=404, detail=f"Product with id [{product_id}] not found")
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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e


@product_router.put("/update_stock/product_id={product_id}&stock_added={stock_added}", status_code=status.HTTP_200_OK)
def update_stock(
    product_id: int,
    stock_added: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],  # admin connecté
):
    """Increase product stock by a given amount (admin only)."""
    productdao = ProductDAO(DBConnector(test=False))
    product_service = ProductService(productdao)
    try:
        added = product_service.increment_stock(product_id=product_id, quantity=stock_added)
        if added:
            return {"message": f"[{stock_added}] was successfully added to the stock of product with id [{product_id}]"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e
