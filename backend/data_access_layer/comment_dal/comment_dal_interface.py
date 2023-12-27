#Author: Vodohleb04
from abc import ABC, abstractmethod
from typing import List, Sequence
from sqlalchemy.orm import Session
from backend.data_layer.mapped_database import Comment
from backend.data_access_layer.comment_dal.save_comment_dto import SaveCommentDTO
from backend.data_access_layer.comment_dal.patch_comment_dto import PatchCommentDTO


class CommentDALInterface(ABC):

    @abstractmethod
    def get_by_id(self, id: int, db_session: Session) -> Comment | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id_list(self, id_list: List[id], db_session: Session) -> Sequence[Comment] | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, comment: SaveCommentDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def patch(self, comment: PatchCommentDTO, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self, id: int, db_session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_id_list(self, id_list: List[id], db_session: Session) -> None:
        raise NotImplementedError
