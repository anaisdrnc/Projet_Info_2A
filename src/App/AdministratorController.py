from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from Model.APIUser import APIUser
from Model.JWTResponse import JWTResponse
from Service.AdminService import AdminService

from .init_app import jwt_service
from .JWTBearer import JWTBearer


if TYPE_CHECKING:
    from Model.Admin import Admin

from pydantic import BaseModel

class AdminUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    username: str | None = None
    password: str | None = None


admin_router = APIRouter(prefix="/admin", tags=["Admin"])
admin_service = AdminService()


@admin_router.post("/jwt", status_code=status.HTTP_201_CREATED)
def login_admin(username: str, password: str) -> JWTResponse:
    """
    Authenticate an admin with username and password and obtain a token
    """
    try:
        admin = admin_service.get_by_username(username)
        if not admin or not admin_service.verify_password(password, admin.password, admin.salt):
            raise Exception("Invalid username or password")
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
        ) from error

    # Encode JWT pour l'admin
    return jwt_service.encode_jwt(admin.id_admin)


@admin_router.get("/me")
def get_admin_own_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> APIUser:
    """
    Get the authenticated admin profile
    """
    return get_admin_from_credentials(credentials)


@admin_router.post("/create", status_code=status.HTTP_201_CREATED)
def create_new_admin(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]
) -> APIUser:
    """
    Create a new admin account (requires JWT authentication).
    """
    # Vérifie que le token est valide
    token = credentials.credentials
    jwt_service.validate_user_jwt(token)

    # Appelle le service
    admin = admin_service.create_admin(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email
    )

    if not admin:
        raise HTTPException(status_code=409, detail="Unable to create admin")

    return APIUser(
        id=admin.id_admin,
        username=admin.user_name,
        first_name=admin.first_name,
        last_name=admin.last_name,
        email=admin.email
    )

@admin_router.put("/me", response_model=APIUser, status_code=status.HTTP_200_OK)
def update_admin_profile(
    payload: AdminUpdateRequest,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]
):
    """
    Update the authenticated admin profile.
    """
    token = credentials.credentials
    admin_id = int(jwt_service.validate_user_jwt(token))
    admin = admin_service.get_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if payload.first_name is not None:
        admin.first_name = payload.first_name

    if payload.last_name is not None:
        admin.last_name = payload.last_name

    if payload.email is not None:
        admin.email = payload.email

    if payload.username is not None:
        admin.user_name = payload.username

    if payload.password is not None:
        # Re-hash du mot de passe avec salt = username
        from utils.securite import hash_password
        admin.salt = admin.user_name
        admin.password = hash_password(payload.password, admin.salt)

    updated = admin_service.update_admin(admin)

    if not updated:
        raise HTTPException(status_code=500, detail="Unable to update admin")

    return APIUser(
        id=admin.id_admin,
        username=admin.user_name,
        first_name=admin.first_name,
        last_name=admin.last_name,
        email=admin.email
    )

def get_admin_from_credentials(
    credentials: HTTPAuthorizationCredentials,
) -> APIUser:
    token = credentials.credentials
    # Récupère l'id_admin encodé dans le JWT
    admin_id = int(jwt_service.validate_user_jwt(token))
    # Récupère l'admin correspondant
    admin = admin_service.get_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return APIUser(id=admin.id_admin, username=admin.user_name, first_name=admin.first_name,
    last_name=admin.last_name, email=admin.email)
