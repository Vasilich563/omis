#Author: Vodohleb04
from backend.data_layer.mapped_database import KnowledgeStatus


class PatchKnowledgeDTO:

    def __init__(
            self, old_title: str,
            status: KnowledgeStatus = None,
            new_title: str = None,
            description: str = None,
            link: str = None,
            category: str = None
    ):
        self.old_title = old_title
        self.status = status
        self.new_title = new_title
        self.description = description
        self.link = link
        self.category = category
