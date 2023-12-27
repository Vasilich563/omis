#Author: Vodohleb04
from typing import Dict
from backend.service_layer.authentication_service.authentication_error import AuthenticationError


class AuthorizationToken:

    def __init__(self, login: str, hashed_password: str, is_admin: bool):
        self.__login = login
        self.__hashed_password = hashed_password
        self.__is_admin = is_admin

    def __check_password(self, hashed_password_to_check: str) -> bool:
        return hashed_password_to_check == self.__hashed_password

    def __check_login(self, login_to_check: str) -> bool:
        return login_to_check == self.__login

    def check_token(self, login_to_check: str, hashed_password_to_check: str) -> bool:
        if not self.__check_login(login_to_check):
            raise AuthenticationError("Login is invalid.")
        if not self.__check_password(hashed_password_to_check):
            raise AuthenticationError("Invalid password.")
        return True

    def get_login(self) -> str:
        return self.__login

    @property
    def is_admin(self) -> bool:
        return self.__is_admin

    def to_json(self) -> Dict:
        return {
            "login": self.__login,
            "hashed_password": self.__hashed_password,
            "is_admin": self.__is_admin
        }
