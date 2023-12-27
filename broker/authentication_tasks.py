#Author: Vodohleb04
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.data_layer.mapped_database import GeneralUser

from backend.data_access_layer.user_dal.user_dal import SQLAlchemyUserDAL
from backend.data_access_layer.user_dal.login_user_dto import LoginUserDTO
from backend.data_access_layer.user_dal.user_dal import SaveUserDTO

from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from backend.service_layer.authentication_service.authentication_service_impl import AuthenticationServiceImpl
from backend.service_layer.authentication_service.authentication_error import AuthenticationError

from broker.celery_broker import broker_app


authentication_service_engine = create_engine("postgresql+psycopg2://postgres:kokakola23@localhost/postgres")
authentication_service_sessionmaker = sessionmaker(authentication_service_engine, expire_on_commit=False)
authentication_service = AuthenticationServiceImpl(SQLAlchemyUserDAL())
print("authentication_service created")


class AuthenticationTasks:
    @staticmethod
    @broker_app.task
    def login_task(request: LoginUserDTO) -> AuthorizationToken | None:
        with authentication_service_sessionmaker.begin() as session:
            try:
                return authentication_service.login(request, session)
            except ValueError:
                return None
            except AuthenticationError:
                return None

    @staticmethod
    @broker_app.task
    def register_task(request: SaveUserDTO) -> AuthorizationToken | None:
        with authentication_service_sessionmaker.begin() as session:
            try:
                return authentication_service.register(request, session)
            except ValueError:
                return None
            except AuthenticationError:
                return None

    @staticmethod
    @broker_app.task
    def get_user_by_login_task(user_login: str) -> GeneralUser | None:
        with authentication_service_sessionmaker.begin() as session:
            return authentication_service.get_user_by_login(user_login, session)
