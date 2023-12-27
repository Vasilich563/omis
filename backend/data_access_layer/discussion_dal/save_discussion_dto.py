# Author: Vodohleb04
class SaveDiscussionDTO:

    def __init__(self, title: str, description: str, category: str, sender_login: str):
        self.title = title
        self.description = description
        self.category = category
        self.sender_login = sender_login
