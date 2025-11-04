from fastapi import APIRouter, HTTPException, status

from src.Model.Order import Order

order_router = APIRouter(prefix="/orders", tags=["Orders"])