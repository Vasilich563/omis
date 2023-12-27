#Author: Vodohleb04
from abc import ABC, abstractmethod
from typing import Sequence, List
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Knowledge
from backend.data_access_layer.knowledge_dal.save_knowledge_dto import SaveKnowledgeDTO
from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from backend.service_layer.authorizable import Authorizable
from backend.data_layer.mapped_database import KnowledgeStatus


class KnowledgeService(Authorizable, ABC):

    @abstractmethod
    def get_knowledge_categories(self, db_session: Session, status: KnowledgeStatus = None) -> List[str] | None:
        raise NotImplementedError

    @abstractmethod
    def get_knowledge_by_title(self, title: str, db_session: Session) -> Knowledge | None:
        raise NotImplementedError

    @abstractmethod
    def get_knowledge_by_category(
            self,
            category: str,
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_knowledge_by_category_list(
            self,
            category_list: List[str],
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_published_knowledge(self, db_session: Session) -> Sequence[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def get_in_processing_knowledge(self, token: AuthorizationToken, db_session: Session) -> Sequence[Knowledge] | None:
        raise NotImplementedError

    @abstractmethod
    def save_knowledge(self, knowledge: SaveKnowledgeDTO, token: AuthorizationToken, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def accept_knowledge_publishing(self, knowledge_title: str, token: AuthorizationToken, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_knowledge_by_title(self, knowledge_title: str, token: AuthorizationToken, db_session: Session) -> None:
        raise NotImplementedError
