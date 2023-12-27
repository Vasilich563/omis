#Author: Vodohleb04
from typing import List, Sequence
from logging import getLogger
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Discussion, Comment
from backend.data_access_layer.comment_dal.save_comment_dto import SaveCommentDTO
from backend.data_access_layer.comment_dal.comment_dal_interface import CommentDALInterface
from backend.data_access_layer.discussion_dal.save_discussion_dto import SaveDiscussionDTO
from backend.data_access_layer.discussion_dal.discussion_dal_interface import DiscussionDALInterface
from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from backend.service_layer.discussion_service.discussion_service import DiscussionService

logger = getLogger(__name__)


class DiscussionServiceImpl(DiscussionService):

    def __init__(self, discussion_dal: DiscussionDALInterface, comment_dal: CommentDALInterface):
        self.__discussion_dal = discussion_dal
        self.__comment_dal = comment_dal

    @staticmethod
    def check_auth_token(authorization_token: AuthorizationToken, requires_admin_rights: bool) -> bool:
        if authorization_token is not None:
            if requires_admin_rights:
                return authorization_token.is_admin
            else:
                return True
        else:
            return False

    def get_discussion_categories(self, db_session: Session) -> List[str] | None:
        return self.__discussion_dal.get_categories(db_session)

    def get_all_discussions(self, db_session: Session) -> Sequence[Discussion] | None:
        return self.__discussion_dal.get_all(db_session)

    def get_discussion_by_title(self, title: str, db_session: Session) -> Discussion | None:
        return self.__discussion_dal.get_by_title(title, db_session)

    def get_discussions_by_category(self, category: str, db_session: Session) -> Sequence[Discussion] | None:
        return self.__discussion_dal.get_by_category(category, db_session)

    def get_discussions_by_category_list(
            self,
            category_list: List[str],
            db_session: Session
    ) -> Sequence[Discussion] | None:
        return self.__discussion_dal.get_by_category_list(category_list, db_session)

    def save_discussion(self, discussion: SaveDiscussionDTO, token: AuthorizationToken, db_session: Session) -> None:
        if self.check_auth_token(token, requires_admin_rights=False) and token.get_login() == discussion.sender_login:
            try:
                self.__discussion_dal.save(discussion, db_session)
            except ValueError as ex:
                logger.warning(ex)

    def delete_discussion_by_title(self, title: str, token: AuthorizationToken, db_session: Session) -> None:
        discussion = self.__discussion_dal.get_by_title(title, db_session)
        if discussion:
            if token.get_login() == discussion.discussion_sender.login:
                token_accepted = self.check_auth_token(token, requires_admin_rights=False)
            else:
                token_accepted = self.check_auth_token(token, requires_admin_rights=True)
            if token_accepted:
                self.__discussion_dal.delete_by_title(title, db_session)

    def get_comment_by_id(self, id: int, db_session: Session) -> Comment | None:
        return self.__comment_dal.get_by_id(id, db_session)

    def save_comment(self, comment: SaveCommentDTO, token: AuthorizationToken, db_session: Session) -> None:
        if self.check_auth_token(token, requires_admin_rights=False) and token.get_login() == comment.sender_login:
            self.__comment_dal.save(comment, db_session)

    def delete_comment_by_id(self, id: int, token: AuthorizationToken, db_session: Session) -> None:
        comment = self.__comment_dal.get_by_id(id, db_session)
        if comment:
            if token.get_login() == comment.comment_sender.login:
                token_accepted = self.check_auth_token(token, requires_admin_rights=False)
            else:
                token_accepted = self.check_auth_token(token, requires_admin_rights=True)
            if token_accepted:
                self.__comment_dal.delete_by_id(id, db_session)


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from sqlalchemy import create_engine
    from backend.data_access_layer.discussion_dal.discussion_dal import SQLAlchemyDiscussionDAL, SaveDiscussionDTO
    from backend.data_access_layer.comment_dal.comment_dal import SQLAlchemyCommentDAL, SaveCommentDTO

    from backend.data_layer.declarative_base import Base


    engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
    #Base.create_from_metadata(engine)
    with Session(engine) as session:
        discussion_dal = SQLAlchemyDiscussionDAL()
        comment_dal = SQLAlchemyCommentDAL()
        discussion_service = DiscussionServiceImpl(discussion_dal, comment_dal)

        discussion_save = SaveDiscussionDTO(
            title="Trash",
            description="How to be a trash",
            category="Police",
            sender_login="user"
        )
        this_token = AuthorizationToken("user", "<PASSWORD>", False)
        other_token = AuthorizationToken("other_user", "pppp", False)
        admin_token = AuthorizationToken("admin", "plan", True)

        #discussion_service.save_discussion(discussion_save, this_token, session)

        knowledge = discussion_service.get_discussion_by_title("Trash", session)

        print(discussion_service.get_discussion_categories(session))

        print(discussion_service.get_discussions_by_category("Police", session))

        #discussion_service.delete_discussion_by_title("Trash", other_token, session)
        #discussion_service.delete_discussion_by_title("Trash", this_token, session)
        #discussion_service.delete_discussion_by_title("Trash", admin_token, session)

        comment_save1 = SaveCommentDTO(
            description="Ti che, plesen, sovsem uhuel?",
            sender_login="other_user",
            discussion_title="Trash"
        )

        comment_save2 = SaveCommentDTO(
            description="Ti che, plesen, sovsem ohrenel?",
            sender_login="other_user",
            discussion_title="Trash"
        )

        comment_save3 = SaveCommentDTO(
            description="ACAB!!!11!",
            sender_login="other_user",
            discussion_title="Trash"
        )

        #discussion_service.save_comment(comment_save1, other_token, session)
        #discussion_service.save_comment(comment_save2, other_token, session)
        #discussion_service.save_comment(comment_save3, other_token, session)
        #discussion_service.delete_comment_by_id(3, admin_token, session)
        #discussion_service.delete_comment_by_id(4, other_token, session)
        #discussion_service.delete_comment_by_id(5, this_token, session)
