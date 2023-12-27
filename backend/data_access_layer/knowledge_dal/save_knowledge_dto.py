# Author: Vodohleb04
class SaveKnowledgeDTO:

    def __init__(self, title: str, description: str, link: str, category: str, sender_login: str):
        self.title = title
        self.description = description
        self.link = link
        self.category = category
        self.sender_login = sender_login
