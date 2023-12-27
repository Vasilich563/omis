#Author: Vodohleb04
class PatchDiscussionDTO:

    def __init__(
            self, old_title: str,
            new_title: str = None, description: str = None, category: str = None, sender_login: str = None
    ):
        self.old_title = old_title
        self.new_title = new_title
        self.description = description
        self.category = category
        self.sender_login = sender_login
