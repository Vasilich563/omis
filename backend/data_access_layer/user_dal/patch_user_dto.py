#Author: Vodohleb04

from datetime import date


class PatchUserDTO:

    def __init__(
            self, login: str,
            username: str = None,
            new_hashed_password: str = None,
            email: str = None,
            birthdate: date = None,
            stack: str = None
    ):
        self.login = login
        self.username = username
        self.new_hashed_password = new_hashed_password
        self.email = email
        self.birthdate = birthdate
        self.stack = stack

