from typing import TYPE_CHECKING, Annotated
from utils.securite import hash_password
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from Service.PasswordService import check_password_strength, create_salt
from Model.APIUser import APIUser
from Model.JWTResponse import JWTResponse
from Service.AdminService import AdminService
from .init_app import jwt_service
from .JWTBearer import JWTBearer
from DAO.AdminDAO import AdminDAO
from DAO.DBConnector import DBConnector

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
def update_my_admin_profile(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]
) -> APIUser:
    """
    Update the authenticated admin's profile.
    All fields are optional, but follow the same structure as create_admin.
    """
    admindao = AdminDAO(DBConnector(test=False))
    admin_service = AdminService(admindao=admindao)
    token = credentials.credentials
    admin_id = int(jwt_service.validate_user_jwt(token))
    print(admin_id)

    # Récupère l'admin actuel
    admin = admin_service.get_by_id(admin_id)
    print(admin)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Met à jour les champs si fournis
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

    # Sauvegarde en DB
    try:
        updated = admin_service.update_admin(admin)
    except HTTPException:
        raise
    except Exception as e:
        print("hello")
        raise HTTPException(status_code=500, detail=str(e))

    if not updated:
        raise HTTPException(status_code=500, detail="Unable to update admin")

    # Retourne le nouvel état
    return APIUser(
        id=admin.id,
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
