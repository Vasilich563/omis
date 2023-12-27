#Author: Vodohleb04
from sqlalchemy import MetaData, text
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    metadata = MetaData(schema='omis2')

    @classmethod
    def create_from_metadata(cls, engine):
        with Session(engine) as session:
            session.execute(text("""CREATE SCHEMA IF NOT EXISTS omis2;"""))
            session.commit()
            cls.metadata.create_all(engine)
            session.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS
                        omis2_user_login_hash_index ON omis2.general_user
                        USING HASH (login);
                    CREATE INDEX IF NOT EXISTS
                        omis2_user_username_hash_index ON omis2.general_user
                        USING HASH (username);
                    CREATE INDEX IF NOT EXISTS
                        omis2_knowledge_title_hash_index ON omis2.knowledge
                        USING HASH (title);
                    CREATE INDEX IF NOT EXISTS
                        omis2_discussion_title_hash_index ON omis2.discussion
                        USING HASH (title);
                    """
                )
            )
            session.commit()

