from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.App.AdministratorController import get_admin_from_credentials
from src.App.JWTBearer import JWTBearer
from src.Model.APIUser import APIUser
from src.Service.DriverService import DriverService

driver_router = APIRouter(prefix="/driver", tags=["Driver"])
driver_service = DriverService()


@driver_router.post("/", status_code=status.HTTP_201_CREATED)
def create_driver(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: str,
    mean_of_transport: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> APIUser:
    """
    Create a new driver account.
    Only an authenticated admin can perform this action.
    Requires a valid admin JWT.
    """
    admin = get_admin_from_credentials(credentials)

    if not admin:
        raise HTTPException(status_code=403, detail="Admin authentication failed")

    driver = driver_service.create_driver(
        username=username,
        password=password,
        firstname=first_name,
        lastname=last_name,
        email=email,
        mean_of_transport=mean_of_transport,
    )

    if not driver:
        raise HTTPException(status_code=400, detail="Driver could not be created")

    return APIUser(
        id=driver.id_driver,
        username=driver.user_name,
        first_name=driver.first_name,
        last_name=driver.last_name,
        email=driver.email,
    )
