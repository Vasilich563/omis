#Author: Vodohleb04
from __future__ import annotations
from typing import List
from datetime import date
from enum import Enum
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.data_layer.declarative_base import Base


class GeneralUser(Base):
    __tablename__ = 'general_user'

    login: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str]
    hashed_password: Mapped[str]
    email: Mapped[str]
    birthdate: Mapped[date]
    stack: Mapped[str]
    _role: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "general_user",
        "polymorphic_on": "_role"
    }

    __table_args__ = (UniqueConstraint("username", name="unique_username"),)

    def get_role(self) -> str:
        return self._role

    def is_admin(self) -> bool:
        return self._role == 'admin'

    def __repr__(self) -> str:
        return (f"GeneralUser(login={self.login}, username={self.username}, hashed_password={self.hashed_password}, "
                f"email={self.email}, birthdate={self.birthdate}, stack={self.stack}, _role={self._role})")

    def __str__(self) -> str:
        return (f"GeneralUser(login: {self.login}, username: {self.username}, email: {self.email}, birthdate: "
                f"{self.birthdate}, stack: {self.stack}, role: {self._role})")

class User(GeneralUser):
    __tablename__ = 'user'

    login: Mapped[str] = mapped_column(ForeignKey("general_user.login", ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "user"
    }
    sent_knowledge: Mapped[List[Knowledge]] = relationship(
        back_populates="knowledge_sender", cascade='all, delete', passive_deletes=True, lazy='selectin'
    )
    sent_discussions: Mapped[List[Discussion]] = relationship(
        back_populates="discussion_sender", cascade='all, delete', passive_deletes=True, lazy='selectin'
    )
    sent_comments: Mapped[List[Comment]] = relationship(
        back_populates="comment_sender", cascade='all, delete', passive_deletes=True, lazy='selectin'
    )


class Admin(GeneralUser):
    __tablename__ = 'admin'

    login: Mapped[str] = mapped_column(ForeignKey("general_user.login", ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin"
    }


class KnowledgeStatus(Enum):
    IN_PROCESSING = "in_processing"
    PUBLISHED = "published"

    def __str__(self) -> str:
        return self.value


class Knowledge(Base):
    __tablename__ = 'knowledge'

    status: Mapped[KnowledgeStatus] = mapped_column(default=KnowledgeStatus.IN_PROCESSING)
    title: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str]
    link: Mapped[str]
    category: Mapped[str]
    sender_login: Mapped[str] = mapped_column(ForeignKey("user.login", ondelete='CASCADE'), nullable=False)

    knowledge_sender: Mapped[User] = relationship(back_populates="sent_knowledge", lazy='selectin')

    def __repr__(self) -> str:
        return (f"Knowledge(title={self.title}, description={self.description}, link={self.link}, "
                f"category={self.category}, sender_login={self.sender_login})")

    def __str__(self) -> str:
        return (f"Knowledge(title: {self.title}, link: {self.link}, category: {self.category}, "
                f"sender_login: {self.sender_login})")


class Discussion(Base):
    __tablename__ = 'discussion'

    title: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str]
    category: Mapped[str]
    sender_login: Mapped[str] = mapped_column(ForeignKey("user.login", ondelete='CASCADE'), nullable=False)

    connected_comments: Mapped[List[Comment]] = relationship(
        back_populates="connected_discussion", lazy='selectin', cascade="all, delete", passive_deletes=True
    )
    discussion_sender: Mapped[User] = relationship(back_populates="sent_discussions", lazy='selectin')

    def __repr__(self) -> str:
        return (f"Discussion(title={self.title}, description={self.description}, category={self.category}"
                f", sender_login={self.sender_login})")

    def __str__(self) -> str:
        return (f"Discussion(title: {self.title}, category: {self.category}, sender_login: "
                f"{self.sender_login})")


class Comment(Base):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(primary_key=True)
    discussion_title: Mapped[int] = mapped_column(
        ForeignKey("discussion.title", ondelete='CASCADE'), nullable=False
    )
    description: Mapped[str]
    sender_login: Mapped[str] = mapped_column(ForeignKey("user.login", ondelete='CASCADE'), nullable=False)

    connected_discussion: Mapped[Discussion] = relationship(back_populates="connected_comments", lazy='selectin')
    comment_sender: Mapped[User] = relationship(back_populates="sent_comments", lazy='selectin')

    def __repr__(self) -> str:
        return f"Comment(id={self.id}, discussion_title={self.discussion_title}, sender_login={self.sender_login})"

    def __str__(self) -> str:
        return f"Comment(id: {self.id}, discussion_title: {self.discussion_title}, sender_login: {self.sender_login})"
