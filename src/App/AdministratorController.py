from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Model.APIUser import APIUser
from src.Model.JWTResponse import JWTResponse
from src.Service.AdminService import AdminService

from .init_app import jwt_service
from .JWTBearer import JWTBearer

if TYPE_CHECKING:
    from src.Model.Admin import Admin

admin_router = APIRouter(prefix="/admin", tags=["Admin"])
admin_service = AdminService()


@admin_router.post("/jwt", status_code=status.HTTP_201_CREATED)
def login_admin(username: str, password: str) -> JWTResponse:
    """
    Authenticate an admin with username and password and obtain a token
    """
    try:
        print(username)
        admin = AdminService.get_by_username(username)
        print("hello" + admin)
        if not admin or not AdminService.verify_password(password, admin.password_hash):
            raise Exception("Invalid username or password")
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
        ) from error

    # Encode JWT pour l'admin
    return jwt_service.encode_jwt(admin.id_admin)


@admin_router.get("/me", dependencies=[Depends(JWTBearer())])
def get_admin_own_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> APIUser:
    """
    Get the authenticated admin profile
    """
    return get_admin_from_credentials(credentials)


def get_admin_from_credentials(
    credentials: HTTPAuthorizationCredentials,
) -> APIUser:
    token = credentials.credentials
    admin_id = int(jwt_service.validate_user_jwt(token))
    admin: "Admin" | None = AdminService.get_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return APIUser(id=admin.id_admin, username=admin.username)
