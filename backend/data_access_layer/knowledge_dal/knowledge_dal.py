#Author: Vodohleb04
import logging
from typing import Sequence, List, Dict
from sqlalchemy import insert, select, update, delete, and_
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from backend.data_access_layer.knowledge_dal.patch_knowledge_dto import PatchKnowledgeDTO
from backend.data_access_layer.knowledge_dal.save_knowledge_dto import SaveKnowledgeDTO
from backend.data_access_layer.knowledge_dal.knowledge_dal_interface import KnowledgeDALInterface
from backend.data_layer.mapped_database import Knowledge, KnowledgeStatus

logger = logging.getLogger(__name__)


class SQLAlchemyKnowledgeDAL(KnowledgeDALInterface):

    def get_categories(self, db_session: Session, status: KnowledgeStatus = None) -> Sequence[str] | None:
        if status is None:
            return db_session.scalars(
                select(Knowledge.category).distinct(Knowledge.category)
            ).all()
        else:
            return db_session.scalars(
                select(Knowledge.category).where(Knowledge.status == status).distinct(Knowledge.category)
            ).all()

    def get_by_title(self, title: str, db_session: Session) -> Knowledge | None:
        return db_session.scalar(
            select(Knowledge).where(Knowledge.title == title).limit(1)
        )

    def get_by_title_list(
            self,
            title_list: List[str],
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        if status is None:
            return db_session.scalars(
                select(Knowledge).where(Knowledge.title.in_(title_list))
            ).all()
        else:
            return db_session.scalars(
                select(Knowledge)
                .where(
                    and_(
                        Knowledge.title.in_(title_list),
                        Knowledge.status == status
                    )
                )
            ).all()

    def get_by_category(
            self,
            category: str,
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        if status is None:
            return db_session.scalars(
                select(Knowledge).where(Knowledge.category == category)
            ).all()
        else:
            return db_session.scalars(
                select(Knowledge)
                .where(
                    and_(Knowledge.category == category, Knowledge.status == status)
                )
            ).all()

    def get_by_category_list(
            self,
            category_list: List[str],
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        if status is None:
            return db_session.scalars(
                select(Knowledge).where(Knowledge.category.in_(category_list))
            ).all()
        else:
            return db_session.scalars(
                select(Knowledge)
                .where(
                    and_(
                        Knowledge.category.in_(category_list),
                        Knowledge.status == status
                    )
                )
            ).all()

    def get_all(self, db_session: Session) -> Sequence[Knowledge] | None:
        return db_session.scalars(select(Knowledge)).all()

    def get_published(self, db_session: Session) -> Sequence[Knowledge] | None:
        return db_session.scalars(
            select(Knowledge).where(Knowledge.status == KnowledgeStatus.PUBLISHED)
        ).all()

    def get_in_processing(self, db_session: Session) -> Sequence[Knowledge] | None:
        return db_session.scalars(
            select(Knowledge).where(Knowledge.status == KnowledgeStatus.IN_PROCESSING)
        ).all()

    def save(self, knowledge: SaveKnowledgeDTO, db_session: Session) -> None:
        if self.get_by_title(knowledge.title, db_session) is None:
            try:
                db_session.execute(
                    insert(Knowledge)
                    .values(
                        title=knowledge.title, description=knowledge.description, link=knowledge.link,
                        category=knowledge.category, sender_login=knowledge.sender_login
                    )
                )
                db_session.commit()
            except DBAPIError as ex:
                db_session.rollback()
                logger.error(
                    f"In save error was occurred: {ex.args[0]}. Knowledge was not saved, transaction "
                    f"was rolled back."
                )
        else:
            logger.error(f"In save error was occurred: Knowledge with title {knowledge.title} already exists.")
            raise ValueError("Knowledge already exists")

    @staticmethod
    def _define_dict_to_update(knowledge: PatchKnowledgeDTO) -> Dict:
        dict_to_update = {}
        if knowledge.status is not None:
            dict_to_update["status"] = knowledge.status
        if knowledge.new_title is not None:
            dict_to_update["title"] = knowledge.new_title
        if knowledge.description is not None:
            dict_to_update["description"] = knowledge.description
        if knowledge.link is not None:
            dict_to_update["link"] = knowledge.link
        if knowledge.category is not None:
            dict_to_update["category"] = knowledge.category
        return dict_to_update

    def patch(self, knowledge: PatchKnowledgeDTO, db_session: Session) -> None:
        if self.get_by_title(knowledge.old_title, db_session):
            try:
                db_session.execute(
                    update(Knowledge)
                    .where(Knowledge.title == knowledge.old_title)
                    .values(**self._define_dict_to_update(knowledge))
                )
                db_session.commit()
            except DBAPIError as ex:
                db_session.rollback()
                logger.error(
                    f"In patch error was occurred: {ex.args[0]}. Knowledge was not patched, transaction "
                    f"was rolled back."
                )

    def delete_by_title(self, title: str, db_session: Session) -> None:
        try:
            db_session.execute(
                delete(Knowledge)
                .where(Knowledge.title == title)
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In delete_by_title error was occurred: {ex.args[0]}. Knowledge was not deleted, transaction "
                f"was rolled back."
            )

    def delete_by_title_list(self, title_list: List[str], db_session: Session) -> None:
        try:
            db_session.execute(
                delete(Knowledge)
                .where(Knowledge.title.in_(title_list))
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In delete_by_title_list error was occurred: {ex.args[0]}. Knowledge were not deleted, transaction "
                f"was rolled back."
            )

    def accept_publishing(self, knowledge_title: str, db_session: Session) -> None:
        patch_knowledge_dto = PatchKnowledgeDTO(knowledge_title, status=KnowledgeStatus.PUBLISHED)
        self.patch(patch_knowledge_dto, db_session)


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from backend.data_layer.declarative_base import Base
    engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
    #Base.create_from_metadata(engine)
    with Session(engine) as session:
        knowledge_dal = SQLAlchemyKnowledgeDAL()
        user_save = SaveKnowledgeDTO(
            title="Fready fazber knowledge",
            description="How to be fready fazber. O holera! Chi to fready fazber? Ow-ow-ow-ow-ow-ow-ow-ow-ow-ow ow-ow-ow-ow ow-ow-ow-ow-ow",
            link="http://fready-fazber.com",
            category="Fready fazber",
            sender_login="user"
        )
        knowledge_dal.save(user_save, session)
        knowledge = knowledge_dal.get_by_title("Fready fazber knowledge", session)
        print(knowledge_dal.get_by_title(knowledge.title, session))
        knowledge_dal.patch(
            PatchKnowledgeDTO(knowledge.title, new_title="Fready Fazber knowledge", category="Hernya"),
            session
        )
        knowledge = knowledge_dal.get_by_title("Fready Fazber knowledge", session)
        print(knowledge)
        print(knowledge_dal.get_categories(session))
        knowledge_dal.accept_publishing(knowledge.title, session)
        print(knowledge_dal.get_by_title("Fready Fazber knowledge", session))
        #knowledge_dal.delete_by_title_list(["Fready Fazber knowledge"])
