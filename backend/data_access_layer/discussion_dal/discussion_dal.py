#Author: Vodohleb04
import logging
from typing import List, Dict, Sequence
from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Discussion
from backend.data_access_layer.discussion_dal.discussion_dal_interface import DiscussionDALInterface
from backend.data_access_layer.discussion_dal.save_discussion_dto import SaveDiscussionDTO
from backend.data_access_layer.discussion_dal.patch_discussion_dto import PatchDiscussionDTO

logger = logging.getLogger(__name__)


class SQLAlchemyDiscussionDAL(DiscussionDALInterface):

    def get_categories(self, db_session: Session) -> Sequence[str] | None:
        return db_session.scalars(
            select(Discussion.category).distinct(Discussion.category)
        ).all()

    def get_all(self, db_session: Session) -> Sequence[Discussion] | None:
        return db_session.scalars(
            select(Discussion)
        ).all()

    def get_by_title(self, title: str, db_session: Session) -> Discussion | None:
        return db_session.scalar(
            select(Discussion)
            .where(Discussion.title == title)
            .limit(1)
        )

    def get_by_title_list(self, title_list: List[str], db_session: Session) -> Sequence[Discussion] | None:
        return db_session.scalars(
            select(Discussion)
            .where(Discussion.title.in_(title_list))
        ).all()

    def get_by_category(self, category: str, db_session: Session) -> Sequence[Discussion] | None:
        return db_session.scalars(
            select(Discussion)
            .where(Discussion.category == category)
        ).all()

    def get_by_category_list(self, category_list: List[str], db_session: Session) -> Sequence[Discussion] | None:
        return db_session.scalars(
            select(Discussion)
            .where(Discussion.category.in_(category_list))
        ).all()

    def save(self, discussion: SaveDiscussionDTO, db_session: Session) -> None:
        if self.get_by_title(discussion.title, db_session) is None:
            try:
                db_session.execute(
                    insert(Discussion)
                    .values(
                        title=discussion.title, description=discussion.description, category=discussion.category,
                        sender_login=discussion.sender_login
                    )
                )
                db_session.commit()
            except DBAPIError as ex:
                db_session.rollback()
                logger.error(
                    f"In save error was occurred: {ex.args[0]}. Discussion wes not saved, transaction "
                    f"was rolled back."
                )
        else:
            logger.error(f"In save error was occurred: Discussion with title {discussion.title} already exists.")
            raise ValueError("Discussion already exists")

    @staticmethod
    def _define_dict_to_update(discussion: PatchDiscussionDTO) -> Dict:
        dict_to_update = {}
        if discussion.new_title is not None:
            dict_to_update["title"] = discussion.new_title
        if discussion.description is not None:
            dict_to_update["description"] = discussion.description
        if discussion.category is not None:
            dict_to_update["category"] = discussion.category
        return dict_to_update

    def patch(self, discussion: PatchDiscussionDTO, db_session: Session) -> None:
        if self.get_by_title(discussion.old_title, db_session):
            try:
                db_session.execute(
                    update(Discussion)
                    .where(Discussion.title == discussion.old_title)
                    .values(**self._define_dict_to_update(discussion))
                )
                db_session.commit()
            except DBAPIError as ex:
                db_session.rollback()
                logger.error(
                    f"In patch error was occurred: {ex.args[0]}. Discussion was not patched, transaction "
                    f"was rolled back."
                )

    def delete_by_title(self, title: str, db_session: Session) -> None:
        try:
            db_session.execute(
                delete(Discussion)
                .where(Discussion.title == title)
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In delete_by_title error was occurred: {ex.args[0]}. Discussion was not deleted, transaction "
                f"was rolled back."
            )

    def delete_by_title_list(self, title_list: List[str], db_session: Session) -> None:
        try:
            db_session.execute(
                delete(Discussion)
                .where(Discussion.title.in_(title_list))
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In delete_by_title_list error was occurred: {ex.args[0]}. Discussions were not deleted, transaction "
                f"was rolled back."
            )


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from backend.data_layer.declarative_base import Base
    engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
    Base.create_from_metadata(engine)
    with Session(engine) as session:
        discussion_dal = SQLAlchemyDiscussionDAL()
        user_save = SaveDiscussionDTO(
            title="Fready fazber discussion",
            description="How to be fready fazber. O holera! Chi to fready fazber? Ow-ow-ow-ow-ow-ow-ow-ow-ow-ow ow-ow-ow-ow ow-ow-ow-ow-ow",
            category="Fready fazber",
            sender_login="user"
        )
        discussion_dal.save(user_save, session)
        discussion = discussion_dal.get_by_title("Fready fazber discussion", session)
        print(discussion_dal.get_by_title(discussion.title, session))
        discussion_dal.patch(
            PatchDiscussionDTO(discussion.title, new_title="Fready Fazber discussion", category="Hernya"),
            session
        )
        discussion = discussion_dal.get_by_title("Fready Fazber discussion", session)
        print(discussion)
        print(discussion_dal.get_by_title("Fready Fazber discussion", session))
        #discussion_dal.delete_by_title_list(["Fready Fazber discussion"])
