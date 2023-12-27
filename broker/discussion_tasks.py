#Author: Vodohleb04
from typing import Sequence, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.data_layer.mapped_database import Discussion, Comment

from backend.data_access_layer.discussion_dal.save_discussion_dto import SaveDiscussionDTO
from backend.data_access_layer.comment_dal.save_comment_dto import SaveCommentDTO
from backend.data_access_layer.discussion_dal.discussion_dal import SQLAlchemyDiscussionDAL
from backend.data_access_layer.comment_dal.comment_dal import SQLAlchemyCommentDAL

from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from backend.service_layer.discussion_service.discussion_service_impl import DiscussionServiceImpl

from broker.celery_broker import broker_app

discussion_service_engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
discussion_service_sessionmaker = sessionmaker(discussion_service_engine, expire_on_commit=False)
discussion_service = DiscussionServiceImpl(SQLAlchemyDiscussionDAL(), SQLAlchemyCommentDAL())


class DiscussionTasks:

    @staticmethod
    @broker_app.task
    def get_discussion_categories_task() -> Sequence[str] | None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.get_discussion_categories(session)

    @staticmethod
    @broker_app.task
    def get_all_discussions_task() -> Sequence[Discussion] | None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.get_all_discussions(session)

    @staticmethod
    @broker_app.task
    def get_discussion_by_title_task(title: str) -> Discussion | None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.get_discussion_by_title(title, session)

    @staticmethod
    @broker_app.task
    def get_discussions_by_category_task(category: str) -> Sequence[Discussion] | None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.get_discussions_by_category(category, session)

    @staticmethod
    @broker_app.task
    def get_discussions_by_category_list_task(category_list: List[str]) -> Sequence[Discussion] | None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.get_discussions_by_category_list(category_list, session)

    @staticmethod
    @broker_app.task
    def save_discussion_task(discussion: SaveDiscussionDTO, token: AuthorizationToken) -> None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.save_discussion(discussion, token, session)

    @staticmethod
    @broker_app.task
    def delete_discussion_by_title_task(title: str, token: AuthorizationToken) -> None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.delete_discussion_by_title(title, token, session)

    @staticmethod
    @broker_app.task
    def get_comment_by_id_task(id: int) -> Comment | None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.get_comment_by_id(id, session)

    @staticmethod
    @broker_app.task
    def save_comment_task(comment: SaveCommentDTO, token: AuthorizationToken) -> None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.save_comment(comment, token, session)

    @staticmethod
    @broker_app.task
    def delete_comment_by_id_task(id: int, token: AuthorizationToken) -> None:
        with discussion_service_sessionmaker.begin() as session:
            return discussion_service.delete_comment_by_id(id, token, session)
