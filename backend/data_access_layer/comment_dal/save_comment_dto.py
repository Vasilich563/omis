#Author: Vodohleb04
class SaveCommentDTO:

    def __init__(self, description: str, sender_login: str, discussion_title: str):
        self.description = description
        self.sender_login = sender_login
        self.discussion_title = discussion_title
