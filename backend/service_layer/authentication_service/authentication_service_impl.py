#Author: Vodohleb04
from sqlalchemy.orm import Session
from backend.data_access_layer.user_dal.login_user_dto import LoginUserDTO
from backend.data_access_layer.user_dal.save_user_dto import SaveUserDTO
from backend.data_layer.mapped_database import GeneralUser
from backend.service_layer.authentication_service.authentication_service import AuthenticationService
from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from backend.data_access_layer.user_dal.user_dal_interface import UserDALInterface


class AuthenticationServiceImpl(AuthenticationService):

    def __init__(self, user_dal: UserDALInterface):
        self.__user_dal = user_dal

    def get_user_by_login(self, user_login: str, db_session: Session) -> GeneralUser:
        return self.__user_dal.get_by_login(user_login, db_session)

    def login(self, request: LoginUserDTO, db_session: Session) -> AuthorizationToken:
        user = self.__user_dal.get_by_login(request.login, db_session)
        if user is None:
            raise ValueError("User does not exist")
        token = AuthorizationToken(login=user.login, hashed_password=user.hashed_password, is_admin=user.is_admin())
        if token.check_token(login_to_check=request.login, hashed_password_to_check=request.hashed_password):
            return token

    def register(self, request: SaveUserDTO, db_session: Session) -> AuthorizationToken:
        self.__user_dal.save(request, db_session)
        # If user already exists Exception (ValueError) will be raised.
        return AuthorizationToken(
            login=request.login, hashed_password=request.hashed_password, is_admin=request.is_admin
        )


if __name__ == "__main__":
    from datetime import date
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from backend.data_layer.declarative_base import Base
    from backend.data_access_layer.user_dal.patch_user_dto import PatchUserDTO
    from backend.data_access_layer.user_dal.user_dal import SQLAlchemyUserDAL
    from backend.service_layer.authentication_service.authentication_error import AuthenticationError
    engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
    #Base.create_from_metadata(engine)
    with Session(engine) as session:
        user_dal = SQLAlchemyUserDAL()
        user_save = SaveUserDTO(
            is_admin=False,
            login="chelick",
            username="Kton-to",
            hashed_password="eto ne ya",
            email="<EMAIL>",
            birthdate=date(year=1965, month=1, day=1),
            stack=""
        )
        wrong_login = LoginUserDTO(
            "user",
            "ssws"
        )
        right_login = LoginUserDTO(
            "user",
            "<PASSWORD>"
        )
        auth_service = AuthenticationServiceImpl(user_dal)
        token = auth_service.register(user_save, session)
        print(token.get_login())
        auth_service.get_user_by_login("user", session)
        print(auth_service.get_user_by_login("user", session))
        #user_dal.patch(PatchUserDTO("user", username="Purple Man", email="5nights@mail.us"), session)
        try:
            auth_service.login(wrong_login, session)
        except AuthenticationError as ex:
            print(ex.args[0])

        try:
            token = auth_service.login(right_login, session)
            print(token.get_login())
        except AuthenticationError as ex:
            print(ex.args[0])
        #user_dal.delete_by_username_list(["Ura Klinskih"], session)

    #token =
