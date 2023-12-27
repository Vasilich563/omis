#Author: Vodohleb04
import logging
from typing import Sequence, List, Dict
from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from backend.data_access_layer.user_dal.patch_user_dto import PatchUserDTO
from backend.data_access_layer.user_dal.save_user_dto import SaveUserDTO
from backend.data_access_layer.user_dal.user_dal_interface import UserDALInterface
from backend.data_layer.mapped_database import GeneralUser, User, Admin

logger = logging.getLogger(__name__)


class SQLAlchemyUserDAL(UserDALInterface):

    def get_by_login(self, user_login: str, db_session: Session) -> GeneralUser | None:
        return db_session.scalar(
            select(GeneralUser)
            .where(GeneralUser.login == user_login)
            .limit(1)
        )

    def get_by_login_list(self, user_login_list: List[str], db_session: Session) -> Sequence[GeneralUser]:
        return db_session.scalars(
            select(GeneralUser)
            .where(
                GeneralUser.login.in_(user_login_list)
            )
        ).all()

    def get_by_username(self, username: str, db_session: Session) -> GeneralUser:
        return db_session.scalar(
            select(GeneralUser)
            .where(GeneralUser.username == username)
            .limit(1)
        )

    def get_by_username_list(self, username_list: List[str], db_session: Session) -> Sequence[GeneralUser]:
        return db_session.scalars(
            select(GeneralUser)
            .where(
                GeneralUser.username.in_(username_list)
            )
        ).all()

    def _save_general_user(self, user: SaveUserDTO, db_session: Session) -> None:
        db_session.execute(
            insert(GeneralUser)
            .values(
                login=user.login, username=user.username, hashed_password=user.hashed_password, email=user.email,
                birthdate=user.birthdate, stack=user.stack, _role="admin" if user.is_admin else "user"
            )
        )

    def _save_admin(self, user: SaveUserDTO, db_session: Session) -> None:
        try:
            self._save_general_user(user, db_session)
            db_session.execute(
                insert(Admin)
                .values(login=user.login)
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(f"In _save_admin error was occurred: {ex.args[0]}. Admin was not saved, transaction was"
                         f"rolled back.")

    def _save_user(self, user: SaveUserDTO, db_session: Session) -> None:
        try:
            self._save_general_user(user, db_session)
            db_session.execute(
                insert(User)
                .values(login=user.login)
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(f"In _save_user error was occurred: {ex.args[0]}. User was not saved, transaction was"
                         f"rolled back.")

    def save(self, user: SaveUserDTO, db_session: Session) -> None:
        if self.get_by_login(user.login, db_session) is None:
            if user.is_admin:
                self._save_admin(user, db_session)
            else:
                self._save_user(user, db_session)
        else:
            logger.error(f"In save error was occurred: user with login {user.login} already exists.")
            raise ValueError("User already exists")

    @staticmethod
    def _define_dict_to_update(user: PatchUserDTO) -> Dict:
        dict_to_update = {}
        if user.username is not None:
            dict_to_update["username"] = user.username
        if user.new_hashed_password is not None:
            dict_to_update["new_hashed_password"] = user.new_hashed_password
        if user.email is not None:
            dict_to_update["email"] = user.email
        if user.birthdate is not None:
            dict_to_update["birthdate"] = user.birthdate
        if user.stack is not None:
            dict_to_update["stack"] = user.stack
        return dict_to_update

    def patch(self, user: PatchUserDTO, db_session: Session) -> None:
        if self.get_by_login(user.login, db_session):
            try:
                db_session.execute(
                    update(GeneralUser)
                    .where(GeneralUser.login == user.login)
                    .values(**self._define_dict_to_update(user))
                )
                db_session.commit()
            except DBAPIError as ex:
                db_session.rollback()
                logger.error(f"In patch error was occurred: {ex.args[0]}. User was not patched, transaction was"
                             f"rolled back.")

    def delete_by_login(self, user_login: str, db_session: Session) -> None:
        try:
            db_session.execute(
                delete(GeneralUser)
                .where(GeneralUser.login == user_login)
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(f"In delete_by_login error was occurred: {ex.args[0]}. User was not deleted, transaction was"
                         f"rolled back.")

    def delete_by_login_list(self, user_login_list: List[str], db_session: Session) -> None:
        try:
            db_session.execute(
                delete(GeneralUser)
                .where(
                    GeneralUser.login.in_(user_login_list)
                )
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(f"In delete_by_login_list error was occurred: {ex.args[0]}. Users were not deleted, "
                         f"transaction was rolled back.")

    def delete_by_username(self, username: str, db_session: Session) -> None:
        try:
            db_session.execute(
                delete(GeneralUser)
                .where(GeneralUser.username == username)
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(f"In delete_by_username error was occurred: {ex.args[0]}. User was not deleted, transaction "
                         f"was rolled back.")

    def delete_by_username_list(self, username_list: List[str], db_session: Session) -> None:
        try:
            db_session.execute(
                delete(GeneralUser)
                .where(
                    GeneralUser.username.in_(username_list)
                )
            )
            db_session.commit()
        except DBAPIError as ex:
            db_session.rollback()
            logger.error(
                f"In delete_by_username_list error was occurred: {ex.args[0]}. Users were not deleted, transaction was"
                f"rolled back."
            )


if __name__ == "__main__":
    from datetime import date
    from sqlalchemy import create_engine
    from backend.data_layer.declarative_base import Base
    engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
    Base.create_from_metadata(engine)
    with Session(engine) as session:
        user_dal = SQLAlchemyUserDAL()
        user_save = SaveUserDTO(
            is_admin=False,
            login="user",
            username="Purple man",
            hashed_password="<PASSWORD>",
            email="<EMAIL>",
            birthdate=date(year=1965, month=1, day=1),
            stack="Guard. Animatronic."
        )
        user_dal.save(user_save, session)
        user_dal.get_by_login("user", session)
        print(user_dal.get_by_login("user", session))
        user_dal.patch(PatchUserDTO("user", username="Purple Man", email="5nights@mail.us"), session)
        print(user_dal.get_by_login("user", session))
        #user_dal.delete_by_username_list(["Ura Klinskih"], session)
