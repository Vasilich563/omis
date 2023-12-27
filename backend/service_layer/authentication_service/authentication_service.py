#Author: Vodohleb04
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import GeneralUser
from backend.data_access_layer.user_dal.save_user_dto import SaveUserDTO
from backend.data_access_layer.user_dal.login_user_dto import LoginUserDTO
from backend.service_layer.authentication_service.authorization_token import AuthorizationToken


class AuthenticationService(ABC):

    @abstractmethod
    def get_user_by_login(self, user_login: str, db_session: Session) -> GeneralUser | None:
        raise NotImplementedError

    @abstractmethod
    def login(self, request: LoginUserDTO, db_session: Session) -> AuthorizationToken:
        raise NotImplementedError

    @abstractmethod
    def register(self, request: SaveUserDTO, db_session: Session) -> AuthorizationToken:
        raise NotImplementedError
