#Author: Vodohleb04
import logging
from typing import Sequence, List
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Knowledge, KnowledgeStatus
from backend.data_access_layer.knowledge_dal.knowledge_dal_interface import KnowledgeDALInterface
from backend.data_access_layer.knowledge_dal.save_knowledge_dto import SaveKnowledgeDTO
from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from backend.service_layer.knowledge_service.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class KnowledgeServiceImpl(KnowledgeService):

    def __init__(self, knowledge_dal: KnowledgeDALInterface):
        self.__knowledge_dal = knowledge_dal

    @staticmethod
    def check_auth_token(authorization_token: AuthorizationToken, requires_admin_rights: bool) -> bool:
        if authorization_token is not None:
            if requires_admin_rights:
                return authorization_token.is_admin
            else:
                return True
        else:
            return False

    def get_knowledge_categories(self, db_session: Session, status: KnowledgeStatus = None) -> List[str] | None:
        return self.__knowledge_dal.get_categories(db_session, status)

    def get_knowledge_by_title(self, title: str, db_session: Session) -> Knowledge | None:
        return self.__knowledge_dal.get_by_title(title, db_session)

    def get_knowledge_by_category(
            self,
            category: str,
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        return self.__knowledge_dal.get_by_category(category, db_session, status=status)

    def get_knowledge_by_category_list(
            self,
            category_list: List[str],
            db_session: Session,
            status: KnowledgeStatus = None
    ) -> Sequence[Knowledge] | None:
        return self.__knowledge_dal.get_by_category_list(category_list, db_session, status=status)

    def get_published_knowledge(self, db_session: Session) -> Sequence[Knowledge] | None:
        return self.__knowledge_dal.get_published(db_session)

    def get_in_processing_knowledge(self, token: AuthorizationToken, db_session: Session) -> Sequence[Knowledge] | None:
        if self.check_auth_token(token, requires_admin_rights=True):
            return self.__knowledge_dal.get_in_processing(db_session)

    def save_knowledge(self, knowledge: SaveKnowledgeDTO, token: AuthorizationToken, db_session: Session) -> None:
        if self.check_auth_token(token, requires_admin_rights=False) and token.get_login() == knowledge.sender_login:
            self.__knowledge_dal.save(knowledge, db_session)

    def accept_knowledge_publishing(self, knowledge_title: str, token: AuthorizationToken, db_session: Session) -> None:
        if self.check_auth_token(token, requires_admin_rights=True):
            self.__knowledge_dal.accept_publishing(knowledge_title, db_session)

    def delete_knowledge_by_title(self, knowledge_title: str, token: AuthorizationToken, db_session: Session) -> None:
        knowledge = self.__knowledge_dal.get_by_title(knowledge_title, db_session)
        if knowledge:
            if token.get_login() == knowledge.knowledge_sender.login:
                token_accepted = self.check_auth_token(token, requires_admin_rights=False)
            else:
                token_accepted = self.check_auth_token(token, requires_admin_rights=True)
            if token_accepted:
                self.__knowledge_dal.delete_by_title(knowledge_title, db_session)


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from sqlalchemy import create_engine
    from backend.data_access_layer.knowledge_dal.knowledge_dal import SQLAlchemyKnowledgeDAL, PatchKnowledgeDTO, SaveKnowledgeDTO

    from backend.data_layer.declarative_base import Base


    engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
    #Base.create_from_metadata(engine)
    with Session(engine) as session:
        knowledge_dal = SQLAlchemyKnowledgeDAL()
        knowledge_service = KnowledgeServiceImpl(knowledge_dal)

        user_save = SaveKnowledgeDTO(
            title="Fready Fazber knowledge",
            description="How to be fready fazber. O holera! Chi to fready fazber? Ow-ow-ow-ow-ow-ow-ow-ow-ow-ow ow-ow-ow-ow ow-ow-ow-ow-ow",
            link="http://fready-fazber.com",
            category="Fready Fazber",
            sender_login="user"
        )
        this_token = AuthorizationToken("user", "<PASSWORD>", False)
        other_token = AuthorizationToken("other_user", "pppp", False)
        admin_token = AuthorizationToken("admin", "plan", True)

        knowledge_service.save_knowledge(user_save, this_token, session)

        knowledge = knowledge_service.get_knowledge_by_title("Fready Fazber knowledge", session)
        print(knowledge_service.get_knowledge_by_title(knowledge.title, session))

        print(knowledge_service.get_knowledge_categories(session))


        #knowledge_service.accept_knowledge_publishing(knowledge.title, this_token, session)
        #knowledge_service.accept_knowledge_publishing(knowledge.title, other_token, session)
        #knowledge_service.accept_knowledge_publishing(knowledge.title, admin_token, session)

        print(knowledge_service.get_knowledge_by_title("Fready Fazber knowledge", session))

        print(knowledge_service.get_knowledge_by_category("Fready Fazber", session))

        print(knowledge_service.get_in_processing_knowledge(this_token, session))
        print(knowledge_service.get_in_processing_knowledge(admin_token, session))


        #knowledge_service.delete_knowledge_by_title("Fready Fazber knowledge", other_token, session)
        #knowledge_service.delete_knowledge_by_title("Fready Fazber knowledge", this_token, session)
        #knowledge_service.delete_knowledge_by_title("Fready Fazber knowledge", admin_token, session)

        print(knowledge_service.get_published_knowledge(session))
