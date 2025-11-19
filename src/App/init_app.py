from dotenv import load_dotenv

from DAO.DBConnector import DBConnector
from DAO.UserRepo import UserRepo
from Service.JWTService import JwtService
from Service.UserService import UserService

load_dotenv()
db_connector = DBConnector()
user_repo = UserRepo(db_connector)
jwt_service = JwtService()
user_service = UserService(user_repo)
