from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Model.Admin import Admin
from src.Model.JWTResponse import JWTResponse
from src.Service.PasswordService import check_password_strength
from src.Service.UserService import UserService

from .init_app import jwt_service  # service pour encoder/valider JWT
from .JWTBearer import JWTBearer

if TYPE_CHECKING:
    from src.Model.Admin import Admin

admin_router = APIRouter(prefix="/admin", tags=["Admins"])

# instance du service Admin
admin_service = UserService()


@admin_router.post("/", status_code=status.HTTP_201_CREATED)
def create_admin(username: str, email: str, password: str) -> Admin:
    """
    Crée un nouvel administrateur après validation du mot de passe
    """
    try:
        check_password_strength(password=password)
    except Exception:
        raise HTTPException(status_code=400, detail="Password too weak") from Exception

    try:
        admin: "Admin" = admin_service.create_admin(username=username, email=email, password=password)
    except Exception as error:
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from error

    return Admin(id=admin.id_admin, username=admin.username, email=admin.email)


@admin_router.post("/jwt", status_code=status.HTTP_201_CREATED)
def login_admin(username: str, password: str) -> JWTResponse:
    """
    Authentifie un administrateur et renvoie un token JWT
    """
    try:
        admin = admin_service.authenticate(username=username, password=password)
        if not admin:
            raise Exception("Invalid credentials")
    except Exception as error:
        raise HTTPException(
            status_code=403, detail="Invalid username and password combination"
        ) from error

    return jwt_service.encode_jwt(admin.id_admin)


@admin_router.get("/me", dependencies=[Depends(JWTBearer())])
def get_admin_own_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> Admin:
    """
    Récupère le profil de l'administrateur connecté
    """
    return get_admin_from_credentials(credentials)


def get_admin_from_credentials(credentials: HTTPAuthorizationCredentials) -> Admin:
    token = credentials.credentials
    admin_id = int(jwt_service.validate_user_jwt(token))
    admin: "Admin" | None = admin_service.get_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return Admin(id=admin.id_admin, username=admin.username, email=admin.email)
