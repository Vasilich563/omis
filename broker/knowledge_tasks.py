#Author: Vodohleb04
from typing import Sequence, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.data_layer.mapped_database import Knowledge, KnowledgeStatus

from backend.data_access_layer.knowledge_dal.save_knowledge_dto import SaveKnowledgeDTO
from backend.data_access_layer.knowledge_dal.knowledge_dal import SQLAlchemyKnowledgeDAL

from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from backend.service_layer.knowledge_service.knowledge_service_impl import KnowledgeServiceImpl

from broker.celery_broker import broker_app


knowledge_service_engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
knowledge_service_sessionmaker = sessionmaker(knowledge_service_engine, expire_on_commit=False)
knowledge_service = KnowledgeServiceImpl(SQLAlchemyKnowledgeDAL())


class KnowledgeTasks:
    @staticmethod
    @broker_app.task
    def get_knowledge_categories_task(status: KnowledgeStatus = None):
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.get_knowledge_categories(session, status=status)

    @staticmethod
    @broker_app.task
    def get_knowledge_by_title_task(title: str) -> Knowledge | None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.get_knowledge_by_title(title, session)

    @staticmethod
    @broker_app.task
    def get_knowledge_by_category_task(category: str, status: KnowledgeStatus = None) -> Sequence[Knowledge] | None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.get_knowledge_by_category(category, session, status=status)

    @staticmethod
    @broker_app.task
    def get_knowledge_by_category_list_task(
            category_list: List[str],
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.get_knowledge_by_category_list(category_list, session, status=status)

    @staticmethod
    @broker_app.task
    def get_published_knowledge_task() -> Sequence[Knowledge] | None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.get_published_knowledge(session)

    @staticmethod
    @broker_app.task
    def get_in_processing_knowledge_task(token: AuthorizationToken) -> Sequence[Knowledge] | None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.get_in_processing_knowledge(token, session)

    @staticmethod
    @broker_app.task
    def save_knowledge_task(knowledge: SaveKnowledgeDTO, token: AuthorizationToken) -> None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.save_knowledge(knowledge, token, session)

    @staticmethod
    @broker_app.task
    def accept_knowledge_publishing_task(knowledge_title: str, token: AuthorizationToken) -> None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.accept_knowledge_publishing(knowledge_title, token, session)

    @staticmethod
    @broker_app.task
    def delete_knowledge_by_title_task(knowledge_title: str, token: AuthorizationToken) -> None:
        with knowledge_service_sessionmaker.begin() as session:
            return knowledge_service.delete_knowledge_by_title(knowledge_title, token, session)
