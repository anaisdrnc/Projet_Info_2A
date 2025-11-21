from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.App.init_app import jwt_service
from src.App.JWTBearer import JWTBearer
from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
from src.Model.APIUser import APIUser
from src.Model.JWTResponse import JWTResponse
from src.Service.AdminService import AdminService
from src.Service.PasswordService import check_password_strength, create_salt
from src.utils.securite import hash_password


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
    Authenticate an admin using username and password.
    Returns a JWT if credentials are valid.
    """
    try:
        admin = admin_service.get_by_username(username)
        if not admin or not admin_service.verify_password(password, admin.password, admin.salt):
            raise Exception("Invalid username or password")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error

    return jwt_service.encode_jwt(admin.id_admin)


@admin_router.get("/me")
def get_admin_own_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> APIUser:
    """
    Return the authenticated admin's profile using the provided JWT.
    """
    return get_admin_from_credentials(credentials)


@admin_router.post("/create", status_code=status.HTTP_201_CREATED)
def create_new_admin(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> APIUser:
    """
    Create a new admin account (requires valid JWT).
    Returns the created admin.
    """
    token = credentials.credentials
    jwt_service.validate_user_jwt(token)

    admin = admin_service.create_admin(
        username=username, password=password, first_name=first_name, last_name=last_name, email=email
    )

    if not admin:
        raise HTTPException(status_code=409, detail="Unable to create admin")

    return APIUser(
        id=admin.id_admin,
        username=admin.user_name,
        first_name=admin.first_name,
        last_name=admin.last_name,
        email=admin.email,
    )


@admin_router.put("/me", response_model=APIUser, status_code=status.HTTP_200_OK)
def update_my_admin_profile(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> APIUser:
    """
    Update the authenticated admin's profile.
    Only provided fields are modified.
    """
    admindao = AdminDAO(DBConnector(test=False))
    admin_service = AdminService(admindao=admindao)
    token = credentials.credentials
    admin_id = int(jwt_service.validate_user_jwt(token))
    print(admin_id)

    admin = admin_service.get_by_id(admin_id)
    print(admin)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if username is not None:
        admin.user_name = username
    if first_name is not None:
        admin.first_name = first_name
    if last_name is not None:
        admin.last_name = last_name
    if email is not None:
        admin.email = email
    if password is not None:
        check_password_strength(password)
        admin.salt = create_salt()
        admin.password = hash_password(password, admin.salt)

    try:
        updated = admin_service.update_admin(admin)
    except HTTPException:
        raise
    except Exception as e:
        print("hello")
        raise HTTPException(status_code=500, detail=str(e)) from e

    if not updated:
        raise HTTPException(status_code=500, detail="Unable to update admin")

    return APIUser(
        id=admin.id, username=admin.user_name, first_name=admin.first_name, last_name=admin.last_name, email=admin.email
    )


def get_admin_from_credentials(
    credentials: HTTPAuthorizationCredentials,
) -> APIUser:
    """
    Extract admin ID from JWT and return the admin profile.
    """
    token = credentials.credentials
    admin_id = int(jwt_service.validate_user_jwt(token))
    admin = admin_service.get_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return APIUser(
        id=admin.id_admin,
        username=admin.user_name,
        first_name=admin.first_name,
        last_name=admin.last_name,
        email=admin.email,
    )
