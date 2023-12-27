#Author: Vodohleb04
from abc import ABC, abstractmethod
from typing import List, Sequence
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Discussion, Comment
from backend.data_access_layer.comment_dal.save_comment_dto import SaveCommentDTO
from backend.data_access_layer.discussion_dal.save_discussion_dto import SaveDiscussionDTO
from backend.service_layer.authorizable import Authorizable
from backend.service_layer.authentication_service.authorization_token import AuthorizationToken


class DiscussionService(Authorizable, ABC):

    @abstractmethod
    def get_discussion_categories(self, db_session: Session) -> Sequence[str] | None:
        raise NotImplementedError

    @abstractmethod
    def get_all_discussions(self, db_session: Session) -> Sequence[Discussion] | None:
        raise NotImplementedError

    @abstractmethod
    def get_discussion_by_title(self, title: str, db_session: Session) -> Discussion | None:
        raise NotImplementedError

    @abstractmethod
    def get_discussions_by_category(self, category: str, db_session: Session) -> Sequence[Discussion] | None:
        raise NotImplementedError

    @abstractmethod
    def get_discussions_by_category_list(
            self,
            category_list: List[str],
            db_session: Session
    ) -> Sequence[Discussion] | None:
        raise NotImplementedError

    @abstractmethod
    def save_discussion(self, discussion: SaveDiscussionDTO, token: AuthorizationToken, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_discussion_by_title(self, title: str, token: AuthorizationToken, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_comment_by_id(self, id: int, db_session: Session) -> Comment | None:
        raise NotImplementedError

    @abstractmethod
    def save_comment(self, comment: SaveCommentDTO, token: AuthorizationToken, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_comment_by_id(self, id: int, token: AuthorizationToken, db_session: Session) -> None:
        raise NotImplementedError
