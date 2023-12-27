#Author: Vodohleb04
from abc import ABC, abstractmethod
from backend.service_layer.authentication_service.authorization_token import AuthorizationToken


class Authorizable(ABC):

    @staticmethod
    @abstractmethod
    def check_auth_token(token: AuthorizationToken, require_admin_rights: bool) -> bool:
        raise NotImplementedError
