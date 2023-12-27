#Author: Vodohleb04
from typing import List, Sequence
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import GeneralUser
from backend.data_access_layer.user_dal.save_user_dto import SaveUserDTO
from backend.data_access_layer.user_dal.patch_user_dto import PatchUserDTO


class UserDALInterface(ABC):

    @abstractmethod
    def get_by_login(self, user_login: str, db_session: Session) -> GeneralUser:
        raise NotImplementedError

    @abstractmethod
    def get_by_login_list(self, user_login_list: List[str], db_session: Session) -> Sequence[GeneralUser]:
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str, db_session: Session) -> GeneralUser:
        raise NotImplementedError

    @abstractmethod
    def get_by_username_list(self, username_list: List[str], db_session: Session) -> Sequence[GeneralUser]:
        raise NotImplementedError

    @abstractmethod
    def save(self, user: SaveUserDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def patch(self, user: PatchUserDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_login(self, user_login: str, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_login_list(self, user_login_list: List[str], db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_username(self, username: str, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_username_list(self, username_list: List[str], db_session: Session) -> None:
        raise NotImplementedError
