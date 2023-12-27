#Author: Vodohleb04
class LoginUserDTO:

    def __init__(self, login: str, hashed_password: str):
        self.login = login
        self.hashed_password = hashed_password

