#Author: Vodohleb04
from abc import ABC, abstractmethod
from typing import List, Sequence
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Discussion
from backend.data_access_layer.discussion_dal.save_discussion_dto import SaveDiscussionDTO
from backend.data_access_layer.discussion_dal.patch_discussion_dto import PatchDiscussionDTO


class DiscussionDALInterface(ABC):

    @abstractmethod
    def get_categories(self, db_session: Session) -> Sequence[str] | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self, db_session: Session) -> Sequence[Discussion] | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_title(self, title: str, db_session: Session) -> Discussion | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_title_list(self, title_list: List[str], db_session: Session) -> Sequence[Discussion] | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_category(self, category: str, db_session: Session) -> Sequence[Discussion] | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_category_list(self, category_list: List[str], db_session: Session) -> Sequence[Discussion] | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, discussion: SaveDiscussionDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def patch(self, discussion: PatchDiscussionDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_title(self, title: str, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_title_list(self, title_list: List[str], db_session: Session) -> None:
        raise NotImplementedError
