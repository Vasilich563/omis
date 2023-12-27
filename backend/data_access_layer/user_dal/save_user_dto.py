#Author: Vodohleb04
from datetime import date


class SaveUserDTO:

    def __init__(
            self, is_admin: bool, login: str, username: str, hashed_password: str, email: str, birthdate: date,
            stack: str = None
    ):
        self.is_admin = is_admin
        self.login = login
        self.username = username
        self.hashed_password = hashed_password
        self.email = email
        self.birthdate = birthdate
        if stack is None:
            self.stack = ""
        else:
            self.stack = stack
