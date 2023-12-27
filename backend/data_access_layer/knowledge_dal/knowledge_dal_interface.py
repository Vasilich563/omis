#Author: Vodohleb04
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Knowledge, KnowledgeStatus
from backend.data_access_layer.knowledge_dal.save_knowledge_dto import SaveKnowledgeDTO
from backend.data_access_layer.knowledge_dal.patch_knowledge_dto import PatchKnowledgeDTO


class KnowledgeDALInterface(ABC):

    @abstractmethod
    def get_categories(self, db_session: Session, status: KnowledgeStatus = None) -> List[str] | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_title(self, title: str, db_session: Session) -> Knowledge | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_title_list(
            self,
            title_list: List[str],
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> List[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_category(
            self,
            category: str,
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> List[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_category_list(
            self,
            category_list: List[str],
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> List[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self, db_session: Session) -> List[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_published(self, db_session: Session) -> List[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_in_processing(self, db_session: Session) -> List[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, knowledge: SaveKnowledgeDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def patch(self, knowledge: PatchKnowledgeDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_title(self, title: str, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_title_list(self, title_list: List[str], db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def accept_publishing(self, knowledge_title: str, db_session: Session) -> None:
        raise NotImplementedError
