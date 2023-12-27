#Author: Vodohleb04
import logging
from typing import List, Dict, Sequence
from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Comment
from backend.data_access_layer.comment_dal.comment_dal_interface import CommentDALInterface
from backend.data_access_layer.comment_dal.save_comment_dto import SaveCommentDTO
from backend.data_access_layer.comment_dal.patch_comment_dto import PatchCommentDTO

logger = logging.getLogger(__name__)


class SQLAlchemyCommentDAL(CommentDALInterface):

    def get_by_id(self, id: int, db_session: Session) -> Comment | None:
        return db_session.scalar(
            select(Comment)
            .where(Comment.id == id)
            .limit(1)
        )

    def get_by_id_list(self, id_list: List[id], db_session: Session) -> Sequence[Comment] | None:
        return db_session.scalars(
            select(Comment)
            .where(Comment.id.in_(id_list))
        ).all()

    def save(self, comment: SaveCommentDTO, db_session: Session) -> None:
        try:
            db_session.execute(
                insert(Comment)
                .values(
                    description=comment.description,
                    sender_login=comment.sender_login,
                    discussion_title=comment.discussion_title
                )
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In save error was occurred: {ex.args[0]}. Comment was not saved, transaction was rolled back."
            )

    @staticmethod
    def _define_dict_to_update(comment: PatchCommentDTO) -> Dict:
        dict_to_update = {}
        if comment.description is not None:
            dict_to_update["description"] = comment.description
        return dict_to_update

    def patch(self, comment: PatchCommentDTO, db_session: Session) -> None:
        if self.get_by_id(comment.id, db_session):
            try:
                db_session.execute(
                    update(Comment)
                    .where(Comment.id == comment.id)
                    .values(**self._define_dict_to_update(comment))
                )
                db_session.commit()
            except DBAPIError as ex:
                db_session.rollback()
                logger.error(
                    f"In patch error was occurred: {ex.args[0]}. Comment was not patched, transaction "
                    f"was rolled back."
                )

    def delete_by_id(self, id: int, db_session: Session) -> None:
        try:
            db_session.execute(
                delete(Comment)
                .where(Comment.id == id)
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In delete_by_id error was occurred: {ex.args[0]}. Comment was not deleted, transaction "
                f"was rolled back."
            )

    def delete_by_id_list(self, id_list: List[id], db_session: Session) -> None:
        try:
            db_session.execute(
                delete(Comment)
                .where(Comment.id.in_(id_list))
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In delete_by_id_list error was occurred: {ex.args[0]}. Comments were not deleted, transaction "
                f"was rolled back."
            )


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from backend.data_layer.declarative_base import Base
    engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
    Base.create_from_metadata(engine)
    with Session(engine) as session:
        comment_dal = SQLAlchemyCommentDAL()
        user_save = SaveCommentDTO(
            description="Hi!",
            sender_login="user",
            discussion_title="Fready Fazber discussion"

        )
        comment_dal.save(user_save, session)
        #comment = comment_dal.get_by_id()
        #print(comment)
        #comment_dal.patch(PatchCommentDTO(comment.id, description="Hello!"))
        #comment = comment_dal.get_by_id(5)
        #print(comment)
        #comment_dal.delete_by_id_list([5])
